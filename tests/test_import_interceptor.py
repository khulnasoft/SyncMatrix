import pytest


def test_syncmatrix_1_import_warning():
    with pytest.raises(ImportError):
        with pytest.warns(UserWarning, match="Attempted import of 'syncmatrix.Client"):
            from syncmatrix import Client  # noqa
