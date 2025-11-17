import pytest

from syncmatrix._internal.compatibility.deprecated import SyncmatrixDeprecationWarning
from syncmatrix.agent import SyncmatrixAgent


def test_agent_emits_deprecation_warning():
    with pytest.warns(
        SyncmatrixDeprecationWarning,
        match=(
            "syncmatrix.agent.SyncmatrixAgent has been deprecated. It will not be available after Sep 2024. Use a worker instead. Refer to the upgrade guide for more information"
        ),
    ):
        SyncmatrixAgent()
