from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from syncmatrix.server.database.dependencies import inject_db
from syncmatrix.server.database.interface import SyncmatrixDBInterface
from syncmatrix.server.schemas import filters, sorting
from syncmatrix.server.schemas.actions import VariableCreate, VariableUpdate


@inject_db
async def create_variable(
    session: AsyncSession,
    variable: VariableCreate,
    db: SyncmatrixDBInterface,
):
    """
    Create a variable

    Args:
        session: async database session
        variable: variable to create

    Returns:
        db.Variable
    """
    model = db.Variable(**variable.dict())
    session.add(model)
    await session.flush()

    return model


@inject_db
async def read_variable(
    session: AsyncSession,
    variable_id: UUID,
    db: SyncmatrixDBInterface,
):
    """
    Reads a variable by id.
    """

    query = sa.select(db.Variable).where(db.Variable.id == variable_id)

    result = await session.execute(query)
    return result.scalar()


@inject_db
async def read_variable_by_name(
    session: AsyncSession,
    name: str,
    db: SyncmatrixDBInterface,
):
    """
    Reads a variable by name.
    """

    query = sa.select(db.Variable).where(db.Variable.name == name)

    result = await session.execute(query)
    return result.scalar()


@inject_db
async def read_variables(
    session: AsyncSession,
    db: SyncmatrixDBInterface,
    variable_filter: Optional[filters.VariableFilter] = None,
    sort: sorting.VariableSort = sorting.VariableSort.NAME_ASC,
    offset: int = None,
    limit: int = None,
):
    """
    Read variables, applying filers.
    """
    query = sa.select(db.Variable).order_by(sort.as_sql_sort(db))

    if variable_filter:
        query = query.where(variable_filter.as_sql_filter(db))

    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    result = await session.execute(query)
    return result.scalars().unique().all()


@inject_db
async def count_variables(
    session: AsyncSession,
    db: SyncmatrixDBInterface,
    variable_filter: Optional[filters.VariableFilter] = None,
) -> int:
    """
    Count variables, applying filters.
    """

    query = sa.select(sa.func.count()).select_from(db.Variable)

    if variable_filter:
        query = query.where(variable_filter.as_sql_filter(db))

    result = await session.execute(query)
    return result.scalar()


@inject_db
async def update_variable(
    session: AsyncSession,
    variable_id: UUID,
    variable: VariableUpdate,
    db: SyncmatrixDBInterface,
) -> bool:
    """
    Updates a variable by id.
    """
    query = (
        sa.update(db.Variable)
        .where(db.Variable.id == variable_id)
        .values(**variable.dict(shallow=True, exclude_unset=True))
    )

    result = await session.execute(query)
    return result.rowcount > 0


@inject_db
async def update_variable_by_name(
    session: AsyncSession,
    name: str,
    variable: VariableUpdate,
    db: SyncmatrixDBInterface,
) -> bool:
    """
    Updates a variable by name.
    """
    query = (
        sa.update(db.Variable)
        .where(db.Variable.name == name)
        .values(**variable.dict(shallow=True, exclude_unset=True))
    )

    result = await session.execute(query)
    return result.rowcount > 0


@inject_db
async def delete_variable(
    session: AsyncSession,
    variable_id: UUID,
    db: SyncmatrixDBInterface,
) -> bool:
    """
    Delete a variable by id.
    """

    query = sa.delete(db.Variable).where(db.Variable.id == variable_id)

    result = await session.execute(query)
    return result.rowcount > 0


@inject_db
async def delete_variable_by_name(
    session: AsyncSession,
    name: str,
    db: SyncmatrixDBInterface,
) -> bool:
    """
    Delete a variable by name.
    """

    query = sa.delete(db.Variable).where(db.Variable.name == name)

    result = await session.execute(query)
    return result.rowcount > 0
