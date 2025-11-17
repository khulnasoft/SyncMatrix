"""
Utilities for Syncmatrix CLI commands
"""
import functools
import traceback

import typer
import typer.core
from click.exceptions import ClickException

from syncmatrix.exceptions import MissingProfileError
from syncmatrix.settings import SYNCMATRIX_TEST_MODE


def exit_with_error(message, code=1, **kwargs):
    """
    Utility to print a stylized error message and exit with a non-zero code
    """
    from syncmatrix.cli.root import app

    kwargs.setdefault("style", "red")
    app.console.print(message, **kwargs)
    raise typer.Exit(code)


def exit_with_success(message, **kwargs):
    """
    Utility to print a stylized success message and exit with a zero code
    """
    from syncmatrix.cli.root import app

    kwargs.setdefault("style", "green")
    app.console.print(message, **kwargs)
    raise typer.Exit(0)


def with_cli_exception_handling(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (typer.Exit, typer.Abort, ClickException):
            raise  # Do not capture click or typer exceptions
        except MissingProfileError as exc:
            exit_with_error(exc)
        except Exception:
            if SYNCMATRIX_TEST_MODE.value():
                raise  # Reraise exceptions during test mode
            traceback.print_exc()
            exit_with_error("An exception occurred.")

    return wrapper
