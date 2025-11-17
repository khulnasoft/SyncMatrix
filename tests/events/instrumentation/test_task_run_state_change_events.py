import pytest

from syncmatrix import flow, task
from syncmatrix.events.clients import AssertingEventsClient
from syncmatrix.events.worker import EventsWorker
from syncmatrix.settings import (
    SYNCMATRIX_EXPERIMENTAL_ENABLE_TASK_SCHEDULING,
    temporary_settings,
)
from syncmatrix.task_server import TaskServer


@pytest.fixture
def enable_task_scheduling():
    with temporary_settings({SYNCMATRIX_EXPERIMENTAL_ENABLE_TASK_SCHEDULING: True}):
        yield


async def test_task_state_change_happy_path(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syncmatrix_client,
):
    @task
    def happy_little_tree():
        return "🌳"

    @flow
    def happy_path():
        return happy_little_tree._run()

    flow_state = happy_path._run()

    task_state = await flow_state.result()
    task_run_id = task_state.state_details.task_run_id
    task_run = await syncmatrix_client.read_task_run(task_run_id)
    task_run_states = await syncmatrix_client.read_task_run_states(task_run_id)

    await asserting_events_worker.drain()
    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    assert len(task_run_states) == len(asserting_events_worker._client.events) == 3

    last_state = None
    for i, task_run_state in enumerate(task_run_states):
        event = asserting_events_worker._client.events[i]

        assert event.id == task_run_state.id
        assert event.occurred == task_run_state.timestamp
        assert event.event == f"syncmatrix.task-run.{task_run_state.name}"
        assert event.payload == {
            "intended": {
                "from": str(last_state.type.value) if last_state else None,
                "to": str(task_run_state.type.value) if task_run_state else None,
            },
            "initial_state": (
                {
                    "type": last_state.type.value,
                    "name": last_state.name,
                    "message": last_state.message or "",
                }
                if last_state
                else None
            ),
            "validated_state": {
                "type": task_run_state.type.value,
                "name": task_run_state.name,
                "message": task_run_state.message or "",
            },
        }
        assert event.follows == (last_state.id if last_state else None)
        assert dict(event.resource.items()) == {
            "syncmatrix.resource.id": f"syncmatrix.task-run.{task_run.id}",
            "syncmatrix.resource.name": task_run.name,
            "syncmatrix.state-message": task_run_state.message or "",
            "syncmatrix.state-name": task_run_state.name,
            "syncmatrix.state-timestamp": task_run_state.timestamp.isoformat(),
            "syncmatrix.state-type": str(task_run_state.type.value),
        }

        last_state = task_run_state


async def test_task_state_change_task_failure(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syncmatrix_client,
):
    @task
    def happy_little_tree():
        raise ValueError("Here's a happy little accident.")

    @flow
    def happy_path():
        return happy_little_tree._run()

    flow_state = happy_path._run()

    task_state = await flow_state.result(raise_on_failure=False)
    task_run_id = task_state.state_details.task_run_id
    task_run = await syncmatrix_client.read_task_run(task_run_id)
    task_run_states = await syncmatrix_client.read_task_run_states(task_run_id)

    await asserting_events_worker.drain()
    assert isinstance(asserting_events_worker._client, AssertingEventsClient)
    assert len(task_run_states) == len(asserting_events_worker._client.events) == 3

    last_state = None
    for i, task_run_state in enumerate(task_run_states):
        event = asserting_events_worker._client.events[i]

        assert event.id == task_run_state.id
        assert event.occurred == task_run_state.timestamp
        assert event.event == f"syncmatrix.task-run.{task_run_state.name}"
        assert event.payload == {
            "intended": {
                "from": str(last_state.type.value) if last_state else None,
                "to": str(task_run_state.type.value) if task_run_state else None,
            },
            "initial_state": (
                {
                    "type": last_state.type.value,
                    "name": last_state.name,
                    "message": last_state.message or "",
                }
                if last_state
                else None
            ),
            "validated_state": {
                "type": task_run_state.type.value,
                "name": task_run_state.name,
                "message": task_run_state.message or "",
            },
        }
        assert event.follows == (last_state.id if last_state else None)
        assert dict(event.resource.items()) == {
            "syncmatrix.resource.id": f"syncmatrix.task-run.{task_run.id}",
            "syncmatrix.resource.name": task_run.name,
            "syncmatrix.state-message": task_run_state.message or "",
            "syncmatrix.state-name": task_run_state.name,
            "syncmatrix.state-timestamp": task_run_state.timestamp.isoformat(),
            "syncmatrix.state-type": str(task_run_state.type.value),
        }

        last_state = task_run_state


async def test_background_task_state_changes(
    asserting_events_worker: EventsWorker,
    reset_worker_events,
    syncmatrix_client,
    enable_task_scheduling,
):
    @task
    def foo():
        pass

    task_run = foo.submit()

    await TaskServer(foo).execute_task_run(task_run)

    task_run_states = await syncmatrix_client.read_task_run_states(task_run.id)

    await asserting_events_worker.drain()

    events = sorted(asserting_events_worker._client.events, key=lambda e: e.occurred)

    assert len(events) == 5  # 4 state changes + 1 block save

    assert len(task_run_states) == 4

    assert [e.event for e in events] == [
        "syncmatrix.task-run.Scheduled",
        "syncmatrix.task-run.Pending",
        "syncmatrix.block.local-file-system.save.called",
        "syncmatrix.task-run.Running",
        "syncmatrix.task-run.Completed",
    ]

    assert [
        (e.payload["intended"]["from"], e.payload["intended"]["to"])
        for e in events
        if e.event.startswith("syncmatrix.task-run.")
    ] == [
        (None, "SCHEDULED"),
        ("SCHEDULED", "PENDING"),
        ("PENDING", "RUNNING"),
        ("RUNNING", "COMPLETED"),
    ]
