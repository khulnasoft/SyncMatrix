from syncmatrix._vendor.fastapi import Depends, Query, status
from syncmatrix._vendor.starlette.exceptions import HTTPException

from syncmatrix.logging import get_logger
from syncmatrix.server import models, schemas
from syncmatrix.server.database.dependencies import provide_database_interface
from syncmatrix.server.database.interface import SyncmatrixDBInterface
from syncmatrix.server.utilities.server import SyncmatrixRouter
from syncmatrix.settings import SYNCMATRIX_SERVER_CSRF_PROTECTION_ENABLED

logger = get_logger("server.api")

router = SyncmatrixRouter(prefix="/csrf-token")


@router.get("")
async def create_csrf_token(
    db: SyncmatrixDBInterface = Depends(provide_database_interface),
    client: str = Query(..., description="The client to create a CSRF token for"),
) -> schemas.core.CsrfToken:
    """Create or update a CSRF token for a client"""
    if SYNCMATRIX_SERVER_CSRF_PROTECTION_ENABLED.value() is False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSRF protection is disabled.",
        )

    async with db.session_context(begin_transaction=True) as session:
        token = await models.csrf_token.create_or_update_csrf_token(
            session=session, client=client
        )
        await models.csrf_token.delete_expired_tokens(session=session)

    return token
