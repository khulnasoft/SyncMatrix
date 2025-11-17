import click
import requests

from syncmatrix import config

from .auth import token_header


@click.group()
def users():
    """
    Interact with Syncmatrix users
    """
    pass
