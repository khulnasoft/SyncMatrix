from syncmatrix.signals import SyncmatrixStateException


def test_exceptions_are_displayed_with_messages():
    err = SyncmatrixStateException("you did something incorrectly")
    assert "you did something incorrectly" in repr(err)
    assert "SyncmatrixStateException" in repr(err)
