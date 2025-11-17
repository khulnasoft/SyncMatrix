"""
Routes for interacting with flow run state objects.
"""

from typing import List
from uuid import UUID

from syncmatrix._vendor.fastapi import Depends, HTTPException, Path, status

import syncmatrix.server.models as models
import syncmatrix.server.schemas as schemas
from syncmatrix.server.database.dependencies import provide_database_interface
from syncmatrix.server.database.interface import SyncmatrixDBInterface
from syncmatrix.server.utilities.server import SyncmatrixRouter

router = SyncmatrixRouter(prefix="/flow_run_states", tags=["Flow Run States"])


@router.get("/{id}")
async def read_flow_run_state(
    flow_run_state_id: UUID = Path(
        ..., description="The flow run state id", alias="id"
    ),
    db: SyncmatrixDBInterface = Depends(provide_database_interface),
) -> schemas.states.State:
    """
    Get a flow run state by id.
    """
    async with db.session_context() as session:
        flow_run_state = await models.flow_run_states.read_flow_run_state(
            session=session, flow_run_state_id=flow_run_state_id
        )
    if not flow_run_state:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Flow run state not found"
        )
    return flow_run_state


@router.get("/")
async def read_flow_run_states(
    flow_run_id: UUID,
    db: SyncmatrixDBInterface = Depends(provide_database_interface),
) -> List[schemas.states.State]:
    """
    Get states associated with a flow run.
    """
    async with db.session_context() as session:
        return await models.flow_run_states.read_flow_run_states(
            session=session, flow_run_id=flow_run_id
        )
