import random

import syncmatrix.exceptions
from syncmatrix.agent import SyncmatrixAgent
from syncmatrix.client.orchestration import SyncmatrixClient
from syncmatrix.client.schemas.actions import WorkPoolCreate
from syncmatrix.client.schemas.objects import WorkPool
from syncmatrix.server.models.workers import DEFAULT_AGENT_WORK_POOL_NAME


async def _safe_get_or_create_workpool(
    client: SyncmatrixClient, *, name: str, type=str
) -> WorkPool:
    try:
        pool = await client.create_work_pool(WorkPoolCreate(name=name, type=type))
    except syncmatrix.exceptions.ObjectAlreadyExists:
        pool = await client.read_work_pool(name)
    return pool


async def test_get_work_queues_returns_default_queues(syncmatrix_client: SyncmatrixClient):
    # create WorkPools to associate with our WorkQueues
    default = await _safe_get_or_create_workpool(
        syncmatrix_client, name=DEFAULT_AGENT_WORK_POOL_NAME, type="syncmatrix-agent"
    )
    ecs = await _safe_get_or_create_workpool(syncmatrix_client, name="ecs", type="ecs")
    agent_pool = await _safe_get_or_create_workpool(
        syncmatrix_client, name="agent", type="syncmatrix-agent"
    )

    # create WorkQueues, associating them with a pool at random
    expected = set()
    for i in range(10):
        random_pool = random.choice([default, ecs, agent_pool])
        q = await syncmatrix_client.create_work_queue(
            name="test-{i}".format(i=i), work_pool_name=random_pool.name
        )
        if random_pool == default:
            expected.add(q.name)

    # create an agent with a prefix that matches all of the created queues
    async with SyncmatrixAgent(work_queue_prefix=["test-"]) as agent:
        results = {q.name async for q in agent.get_work_queues()}

    # verify that only WorkQueues with in the default pool are returned for
    # this agent since it does not have a work pool name
    assert results == expected
