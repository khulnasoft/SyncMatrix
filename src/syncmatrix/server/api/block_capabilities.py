"""
Routes for interacting with block capabilities.
"""
from typing import List

from syncmatrix._vendor.fastapi import Depends

from syncmatrix.server import models
from syncmatrix.server.database.dependencies import (
    SyncmatrixDBInterface,
    provide_database_interface,
)
from syncmatrix.server.utilities.server import SyncmatrixRouter

router = SyncmatrixRouter(prefix="/block_capabilities", tags=["Block capabilities"])


@router.get("/")
async def read_available_block_capabilities(
    db: SyncmatrixDBInterface = Depends(provide_database_interface),
) -> List[str]:
    async with db.session_context() as session:
        return await models.block_schemas.read_available_block_capabilities(
            session=session
        )
