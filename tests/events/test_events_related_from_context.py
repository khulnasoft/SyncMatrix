from contextlib import ExitStack
from unittest import mock

import pytest

from syncmatrix import flow, task
from syncmatrix.client.orchestration import get_client
from syncmatrix.context import FlowRunContext
from syncmatrix.events.related import (
    MAX_CACHE_SIZE,
    _get_and_cache_related_object,
    related_resources_from_run_context,
)
from syncmatrix.events.schemas import RelatedResource
from syncmatrix.states import Running


@pytest.fixture
async def spy_client(test_database_connection_url):
    async with get_client() as client:
        exit_stack = ExitStack()

        for method in [
            "read_flow",
            "read_flow_run",
            "read_deployment",
            "read_work_queue",
            "read_work_pool",
        ]:
            exit_stack.enter_context(
                mock.patch.object(client, method, wraps=getattr(client, method)),
            )

        class NoOpClientWrapper:
            def __init__(self, client):
                self.client = client

            async def __aenter__(self):
                return self.client

            async def __aexit__(self, *args):
                pass

        yield NoOpClientWrapper(client)

        exit_stack.close()


async def test_gracefully_handles_missing_context():
    related = await related_resources_from_run_context()
    assert related == []


async def test_gets_related_from_run_context(
    syncmatrix_client, work_queue_1, worker_deployment_wq1
):
    flow_run = await syncmatrix_client.create_flow_run_from_deployment(
        worker_deployment_wq1.id,
        state=Running(),
        tags=["flow-run-one"],
    )

    with FlowRunContext.construct(flow_run=flow_run):
        related = await related_resources_from_run_context()

    work_pool = work_queue_1.work_pool
    db_flow = await syncmatrix_client.read_flow(flow_run.flow_id)

    assert related == [
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.flow-run.{flow_run.id}",
                "syncmatrix.resource.role": "flow-run",
                "syncmatrix.resource.name": flow_run.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.flow.{db_flow.id}",
                "syncmatrix.resource.role": "flow",
                "syncmatrix.resource.name": db_flow.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.deployment.{worker_deployment_wq1.id}",
                "syncmatrix.resource.role": "deployment",
                "syncmatrix.resource.name": worker_deployment_wq1.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.work-queue.{work_queue_1.id}",
                "syncmatrix.resource.role": "work-queue",
                "syncmatrix.resource.name": work_queue_1.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.work-pool.{work_pool.id}",
                "syncmatrix.resource.role": "work-pool",
                "syncmatrix.resource.name": work_pool.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": "syncmatrix.tag.flow-run-one",
                "syncmatrix.resource.role": "tag",
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": "syncmatrix.tag.test",
                "syncmatrix.resource.role": "tag",
            }
        ),
    ]


async def test_can_exclude_by_resource_id(syncmatrix_client):
    @flow
    async def test_flow():
        flow_run_context = FlowRunContext.get()
        assert flow_run_context is not None
        exclude = {f"syncmatrix.flow-run.{flow_run_context.flow_run.id}"}

        return await related_resources_from_run_context(exclude=exclude)

    state = await test_flow._run()

    flow_run = await syncmatrix_client.read_flow_run(state.state_details.flow_run_id)

    related = await state.result()

    assert f"syncmatrix.flow-run.{flow_run.id}" not in related


async def test_gets_related_from_task_run_context(syncmatrix_client):
    @task
    async def test_task():
        # Clear the FlowRunContext to simulated a task run in a remote worker.
        FlowRunContext.__var__.set(None)
        return await related_resources_from_run_context()

    @flow
    async def test_flow():
        return await test_task._run()

    state = await test_flow._run()
    task_state = await state.result()

    flow_run = await syncmatrix_client.read_flow_run(state.state_details.flow_run_id)
    db_flow = await syncmatrix_client.read_flow(flow_run.flow_id)
    task_run = await syncmatrix_client.read_task_run(task_state.state_details.task_run_id)

    related = await task_state.result()

    assert related == [
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.flow-run.{flow_run.id}",
                "syncmatrix.resource.role": "flow-run",
                "syncmatrix.resource.name": flow_run.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.task-run.{task_run.id}",
                "syncmatrix.resource.role": "task-run",
                "syncmatrix.resource.name": task_run.name,
            }
        ),
        RelatedResource(
            __root__={
                "syncmatrix.resource.id": f"syncmatrix.flow.{db_flow.id}",
                "syncmatrix.resource.role": "flow",
                "syncmatrix.resource.name": db_flow.name,
            }
        ),
    ]


async def test_caches_related_objects(spy_client):
    @flow
    async def test_flow():
        flow_run_context = FlowRunContext.get()
        assert flow_run_context is not None

        with mock.patch("syncmatrix.client.orchestration.get_client", lambda: spy_client):
            await related_resources_from_run_context()
            await related_resources_from_run_context()

    await test_flow()

    spy_client.client.read_flow.assert_called_once()


async def test_lru_cache_evicts_oldest():
    cache = {}

    async def fetch(obj_id):
        return obj_id

    await _get_and_cache_related_object("flow-run", "flow-run", fetch, "👴", cache)
    assert "flow-run.👴" in cache

    await _get_and_cache_related_object("flow-run", "flow-run", fetch, "👩", cache)
    assert "flow-run.👴" in cache

    for i in range(MAX_CACHE_SIZE):
        await _get_and_cache_related_object(
            "flow-run", "flow-run", fetch, f"👶 {i}", cache
        )

    assert "flow-run.👴" not in cache


async def test_lru_cache_timestamp_updated():
    cache = {}

    async def fetch(obj_id):
        return obj_id

    await _get_and_cache_related_object("flow-run", "flow-run", fetch, "👴", cache)
    _, timestamp = cache["flow-run.👴"]

    await _get_and_cache_related_object("flow-run", "flow-run", fetch, "👴", cache)
    _, next_timestamp = cache["flow-run.👴"]

    assert next_timestamp > timestamp
