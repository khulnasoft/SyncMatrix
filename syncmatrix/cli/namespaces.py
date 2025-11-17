import click
import requests

import syncmatrix

# server = syncmatrix.config.get('syncmatrix', 'server_address')
# api_url = server + '/project'


@click.group()
def projects():
    """
    Interact with Syncmatrix projects
    """
    pass


@projects.command()
def list():
    response = requests.get(api_url, headers=syncmatrix.cli.auth.token_header())
    click.echo({"status": response.status_code, "result": response.json()})
