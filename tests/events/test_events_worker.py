import uuid

import pytest

from syncmatrix import flow
from syncmatrix.events import Event
from syncmatrix.events.clients import (
    AssertingEventsClient,
    NullEventsClient,
    SyncmatrixCloudEventsClient,
)
from syncmatrix.events.worker import EventsWorker
from syncmatrix.settings import (
    SYNCMATRIX_API_URL,
    SYNCMATRIX_CLOUD_API_URL,
    SYNCMATRIX_EXPERIMENTAL_ENABLE_EVENTS_CLIENT,
    temporary_settings,
)


@pytest.fixture
def event() -> Event:
    return Event(
        event="vogon.poetry.read",
        resource={"syncmatrix.resource.id": f"poem.{uuid.uuid4()}"},
    )


def test_emits_event_via_client(asserting_events_worker: EventsWorker, event: Event):
    asserting_events_worker.send(event)

    asserting_events_worker.drain()

    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    assert asserting_events_worker._client.events == [event]


def test_worker_instance_null_client_no_api_url():
    with temporary_settings(updates={SYNCMATRIX_API_URL: None}):
        worker = EventsWorker.instance()
        assert worker.client_type == NullEventsClient


def test_worker_instance_null_client_non_cloud_api_url():
    with temporary_settings(updates={SYNCMATRIX_API_URL: "http://localhost:8080/api"}):
        worker = EventsWorker.instance()
        assert worker.client_type == NullEventsClient


def test_worker_instance_null_client_cloud_api_url_experiment_disabled():
    with temporary_settings(
        updates={
            SYNCMATRIX_EXPERIMENTAL_ENABLE_EVENTS_CLIENT: False,
            SYNCMATRIX_API_URL: "https://api.syncmatrix.cloud/api/accounts/72483643-e98d-4323-889a-a12905ff21cd/workspaces/cda37001-1181-4f3c-bf03-00da4b532776",
            SYNCMATRIX_CLOUD_API_URL: "https://api.syncmatrix.cloud/api/",
        }
    ):
        worker = EventsWorker.instance()
        assert worker.client_type == NullEventsClient


def test_worker_instance_null_client_cloud_api_url_experiment_enabled():
    with temporary_settings(
        updates={
            SYNCMATRIX_EXPERIMENTAL_ENABLE_EVENTS_CLIENT: True,
            SYNCMATRIX_API_URL: "https://api.syncmatrix.cloud/api/accounts/72483643-e98d-4323-889a-a12905ff21cd/workspaces/cda37001-1181-4f3c-bf03-00da4b532776",
            SYNCMATRIX_CLOUD_API_URL: "https://api.syncmatrix.cloud/api/",
        }
    ):
        worker = EventsWorker.instance()
        assert worker.client_type == SyncmatrixCloudEventsClient


async def test_includes_related_resources_from_run_context(
    asserting_events_worker: EventsWorker, reset_worker_events, syncmatrix_client
):
    @flow
    def emitting_flow():
        from syncmatrix.events import emit_event

        emit_event(
            event="vogon.poetry.read",
            resource={"syncmatrix.resource.id": "vogon.poem.oh-freddled-gruntbuggly"},
        )

    state = emitting_flow._run()

    flow_run = await syncmatrix_client.read_flow_run(state.state_details.flow_run_id)
    db_flow = await syncmatrix_client.read_flow(flow_run.flow_id)

    asserting_events_worker.drain()

    assert len(asserting_events_worker._client.events) == 1
    event = asserting_events_worker._client.events[0]
    assert event.event == "vogon.poetry.read"
    assert event.resource.id == "vogon.poem.oh-freddled-gruntbuggly"

    assert len(event.related) == 2

    assert event.related[0].id == f"syncmatrix.flow-run.{flow_run.id}"
    assert event.related[0].role == "flow-run"
    assert event.related[0]["syncmatrix.resource.name"] == flow_run.name

    assert event.related[1].id == f"syncmatrix.flow.{db_flow.id}"
    assert event.related[1].role == "flow"
    assert event.related[1]["syncmatrix.resource.name"] == db_flow.name
