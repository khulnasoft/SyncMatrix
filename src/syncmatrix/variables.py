from typing import Optional

from syncmatrix.client.orchestration import SyncmatrixClient
from syncmatrix.client.utilities import get_or_create_client
from syncmatrix.utilities.asyncutils import sync_compatible


@sync_compatible
async def get(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a variable by name. If doesn't exist return the default.
    ```
        from syncmatrix import variables

        @flow
        def my_flow():
            var = variables.get("my_var")
    ```
    or
    ```
        from syncmatrix import variables

        @flow
        async def my_flow():
            var = await variables.get("my_var")
    ```
    """
    variable = await _get_variable_by_name(name)
    return variable.value if variable else default


async def _get_variable_by_name(
    name: str,
    client: Optional[SyncmatrixClient] = None,
):
    client, _ = get_or_create_client(client)
    variable = await client.read_variable_by_name(name)
    return variable
