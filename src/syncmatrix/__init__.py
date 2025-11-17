# isort: skip_file

# Setup version and path constants

from . import _version
import importlib
import pathlib
import warnings
import sys

__version_info__ = _version.get_versions()
__version__ = __version_info__["version"]

# The absolute path to this module
__module_path__ = pathlib.Path(__file__).parent
# The absolute path to the root of the repository, only valid for use during development
__development_base_path__ = __module_path__.parents[1]

# The absolute path to the built UI within the Python module, used by
# `syncmatrix server start` to serve a dynamic build of the UI
__ui_static_subpath__ = __module_path__ / "server" / "ui_build"

# The absolute path to the built UI within the Python module
__ui_static_path__ = __module_path__ / "server" / "ui"

del _version, pathlib

if sys.version_info < (3, 8):
    warnings.warn(
        (
            "Syncmatrix dropped support for Python 3.7 when it reached end-of-life"
            " . To use new versions of Syncmatrix, you will need"
            " to upgrade to Python 3.8+. See https://devguide.python.org/versions/ for "
            " more details."
        ),
        FutureWarning,
        stacklevel=2,
    )


# Import user-facing API
from syncmatrix.runner import Runner, serve
from syncmatrix.deployments import deploy
from syncmatrix.states import State
from syncmatrix.logging import get_run_logger
from syncmatrix.flows import flow, Flow
from syncmatrix.tasks import task, Task
from syncmatrix.context import tags
from syncmatrix.manifests import Manifest
from syncmatrix.utilities.annotations import unmapped, allow_failure
from syncmatrix.results import BaseResult
from syncmatrix.engine import pause_flow_run, resume_flow_run, suspend_flow_run
from syncmatrix.client.orchestration import get_client, SyncmatrixClient
from syncmatrix.client.cloud import get_cloud_client, CloudClient
import syncmatrix.variables
import syncmatrix.runtime

# Import modules that register types
import syncmatrix.serializers
import syncmatrix.deprecated.data_documents
import syncmatrix.deprecated.packaging
import syncmatrix.blocks.kubernetes
import syncmatrix.blocks.notifications
import syncmatrix.blocks.system
import syncmatrix.infrastructure.process
import syncmatrix.infrastructure.kubernetes
import syncmatrix.infrastructure.container

# Initialize the process-wide profile and registry at import time
import syncmatrix.context

syncmatrix.context.initialize_object_registry()

# Perform any forward-ref updates needed for Pydantic models
import syncmatrix.client.schemas

syncmatrix.context.FlowRunContext.update_forward_refs(Flow=Flow)
syncmatrix.context.TaskRunContext.update_forward_refs(Task=Task)
syncmatrix.client.schemas.State.update_forward_refs(
    BaseResult=BaseResult, DataDocument=syncmatrix.deprecated.data_documents.DataDocument
)
syncmatrix.client.schemas.StateCreate.update_forward_refs(
    BaseResult=BaseResult, DataDocument=syncmatrix.deprecated.data_documents.DataDocument
)


syncmatrix.plugins.load_extra_entrypoints()

# Configure logging
import syncmatrix.logging.configuration

syncmatrix.logging.configuration.setup_logging()
syncmatrix.logging.get_logger("profiles").debug(
    f"Using profile {syncmatrix.context.get_settings_context().profile.name!r}"
)

# Ensure moved names are accessible at old locations
import syncmatrix.client

syncmatrix.client.get_client = get_client
syncmatrix.client.SyncmatrixClient = SyncmatrixClient


from syncmatrix._internal.compatibility.deprecated import (
    inject_renamed_module_alias_finder,
    register_renamed_module,
)

register_renamed_module(
    "syncmatrix.client.orchestration",
    "syncmatrix.client.orchestration",
    start_date="Feb 2023",
)
register_renamed_module(
    "syncmatrix.docker",
    "syncmatrix.utilities.dockerutils",
    start_date="Mar 2023",
)
register_renamed_module(
    "syncmatrix.infrastructure.docker",
    "syncmatrix.infrastructure.container",
    start_date="Mar 2023",
)
register_renamed_module(
    "syncmatrix.projects", "syncmatrix.deployments", start_date="Jun 2023"
)
register_renamed_module(
    "syncmatrix.packaging", "syncmatrix.deprecated.packaging", start_date="Mar 2024"
)
inject_renamed_module_alias_finder()


# Attempt to warn users who are importing Syncmatrix 1.x attributes that they may
# have accidentally installed Syncmatrix 2.x

SYNCMATRIX_1_ATTRIBUTES = [
    "syncmatrix.Client",
    "syncmatrix.Parameter",
    "syncmatrix.api",
    "syncmatrix.apply_map",
    "syncmatrix.case",
    "syncmatrix.config",
    "syncmatrix.context",
    "syncmatrix.flatten",
    "syncmatrix.mapped",
    "syncmatrix.models",
    "syncmatrix.resource_manager",
]


class Syncmatrix1ImportInterceptor(importlib.abc.Loader):
    def find_spec(self, fullname, path, target=None):
        if fullname in SYNCMATRIX_1_ATTRIBUTES:
            warnings.warn(
                f"Attempted import of {fullname!r}, which is part of Syncmatrix 1.x, while"
                f" Syncmatrix {__version__} is installed. If you're upgrading you'll need"
                " to update your code, see the Syncmatrix 2.x migration guide:"
                " `https://orion-docs.khulnasoft.com/migration_guide/`. Otherwise ensure"
                " that your code is pinned to the expected version."
            )


if not hasattr(sys, "frozen"):
    sys.meta_path.insert(0, Syncmatrix1ImportInterceptor())


# Declare API for type-checkers
__all__ = [
    "allow_failure",
    "flow",
    "Flow",
    "get_client",
    "get_run_logger",
    "Manifest",
    "State",
    "tags",
    "task",
    "Task",
    "unmapped",
    "Runner",
    "serve",
    "deploy",
    "pause_flow_run",
    "resume_flow_run",
    "suspend_flow_run",
]
