"""
DEPRECATION WARNING:
This module is deprecated as of March 2024 and will not be available after September 2024.
"""

from uuid import UUID

from syncmatrix._internal.compatibility.deprecated import deprecated_class
from syncmatrix._internal.pydantic import HAS_PYDANTIC_V2

if HAS_PYDANTIC_V2:
    from pydantic.v1 import Field
else:
    from pydantic import Field

from typing_extensions import Literal

from syncmatrix.blocks.core import Block
from syncmatrix.client.orchestration import SyncmatrixClient
from syncmatrix.client.utilities import inject_client
from syncmatrix.deprecated.packaging.base import PackageManifest, Packager, Serializer
from syncmatrix.deprecated.packaging.serializers import SourceSerializer
from syncmatrix.filesystems import LocalFileSystem, ReadableFileSystem, WritableFileSystem
from syncmatrix.flows import Flow
from syncmatrix.settings import SYNCMATRIX_HOME
from syncmatrix.utilities.hashing import stable_hash


@deprecated_class(start_date="Mar 2024")
class FilePackageManifest(PackageManifest):
    """
    DEPRECATION WARNING:

    This class is deprecated as of version March 2024 and will not be available after September 2024.
    """

    type: Literal["file"] = "file"
    serializer: Serializer
    key: str
    filesystem_id: UUID

    @inject_client
    async def unpackage(self, client: SyncmatrixClient) -> Flow:
        block_document = await client.read_block_document(self.filesystem_id)
        filesystem: ReadableFileSystem = Block._from_block_document(block_document)
        content = await filesystem.read_path(self.key)
        return self.serializer.loads(content)


@deprecated_class(start_date="Mar 2024")
class FilePackager(Packager):
    """
    DEPRECATION WARNING:

    This class is deprecated as of version March 2024 and will not be available after September 2024.

    This packager stores the flow as a single file.

    By default, the file is the source code of the module the flow is defined in.
    Alternative serialization modes are available in `syncmatrix.deprecated.packaging.serializers`.
    """

    type: Literal["file"] = "file"
    serializer: Serializer = Field(default_factory=SourceSerializer)
    filesystem: WritableFileSystem = Field(
        default_factory=lambda: LocalFileSystem(
            basepath=SYNCMATRIX_HOME.value() / "storage"
        )
    )

    @inject_client
    async def package(self, flow: Flow, client: "SyncmatrixClient") -> FilePackageManifest:
        content = self.serializer.dumps(flow)
        key = stable_hash(content)

        await self.filesystem.write_path(key, content)

        filesystem_id = (
            self.filesystem._block_document_id
            or await self.filesystem._save(is_anonymous=True)
        )

        return self.base_manifest(flow).finalize(
            serializer=self.serializer,
            filesystem_id=filesystem_id,
            key=key,
        )
