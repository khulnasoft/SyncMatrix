"""
Deprecated - Command line interface for working with projects.
"""
from pathlib import Path
from typing import List

import typer
import yaml
from rich.table import Table

import syncmatrix
from syncmatrix._internal.compatibility.deprecated import generate_deprecation_message
from syncmatrix.cli._prompts import prompt_select_from_table
from syncmatrix.cli._types import SyncmatrixTyper
from syncmatrix.cli._utilities import exit_with_error
from syncmatrix.cli.root import app, is_interactive
from syncmatrix.client.orchestration import get_client
from syncmatrix.deployments import find_syncmatrix_directory, initialize_project
from syncmatrix.deployments import register_flow as register
from syncmatrix.deployments.steps.core import run_steps
from syncmatrix.exceptions import ObjectNotFound

# Deprecated compatibility
project_app = SyncmatrixTyper(
    name="project",
    help="Deprecated. Use `syncmatrix init` instead.",
    deprecated=True,
    deprecated_name="syncmatrix project",
    deprecated_start_date="Jun 2023",
    deprecated_help="Use `syncmatrix` instead.",
)
app.add_typer(project_app, aliases=["projects"])

recipe_app = SyncmatrixTyper(
    name="recipe",
    help="Deprecated. Use `syncmatrix init` instead.",
    deprecated=True,
    deprecated_name="syncmatrix project recipe",
    deprecated_start_date="Jun 2023",
    deprecated_help="Use `syncmatrix init` instead.",
)
project_app.add_typer(recipe_app, aliases=["recipes"])


@recipe_app.command()
async def ls():
    """
    List available recipes.
    """

    recipe_paths = syncmatrix.__module_path__ / "deployments" / "recipes"
    recipes = {}

    for recipe in recipe_paths.iterdir():
        if recipe.is_dir() and (recipe / "syncmatrix.yaml").exists():
            with open(recipe / "syncmatrix.yaml") as f:
                recipes[recipe.name] = yaml.safe_load(f).get(
                    "description", "(no description available)"
                )

    table = Table(
        title="Available project recipes",
        caption=(
            "Run `syncmatrix project init --recipe <recipe>` to initialize a project with"
            " a recipe."
        ),
        caption_style="red",
    )
    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Description", justify="left", style="white", no_wrap=False)
    for name, description in sorted(recipes.items(), key=lambda x: x[0]):
        table.add_row(name, description)

    app.console.print(table)


@project_app.command()
@app.command()
async def init(
    name: str = None,
    recipe: str = None,
    fields: List[str] = typer.Option(
        None,
        "-f",
        "--field",
        help=(
            "One or more fields to pass to the recipe (e.g., image_name) in the format"
            " of key=value."
        ),
    ),
):
    """
    Initialize a new project.
    """
    inputs = {}
    fields = fields or []
    recipe_paths = syncmatrix.__module_path__ / "deployments" / "recipes"

    for field in fields:
        key, value = field.split("=")
        inputs[key] = value

    if not recipe and is_interactive():
        recipe_paths = syncmatrix.__module_path__ / "deployments" / "recipes"
        recipes = []

        for r in recipe_paths.iterdir():
            if r.is_dir() and (r / "syncmatrix.yaml").exists():
                with open(r / "syncmatrix.yaml") as f:
                    recipe_data = yaml.safe_load(f)
                    recipe_name = r.name
                    recipe_description = recipe_data.get(
                        "description", "(no description available)"
                    )
                    recipe_dict = {
                        "name": recipe_name,
                        "description": recipe_description,
                    }
                    recipes.append(recipe_dict)

        selected_recipe = prompt_select_from_table(
            app.console,
            "Would you like to initialize your deployment configuration with a recipe?",
            columns=[
                {"header": "Name", "key": "name"},
                {"header": "Description", "key": "description"},
            ],
            data=recipes,
            opt_out_message="No, I'll use the default deployment configuration.",
            opt_out_response={},
        )
        if selected_recipe != {}:
            recipe = selected_recipe["name"]

    if recipe and (recipe_paths / recipe / "syncmatrix.yaml").exists():
        with open(recipe_paths / recipe / "syncmatrix.yaml") as f:
            recipe_inputs = yaml.safe_load(f).get("required_inputs") or {}

        if recipe_inputs:
            if set(recipe_inputs.keys()) < set(inputs.keys()):
                # message to user about extra fields
                app.console.print(
                    (
                        f"Warning: extra fields provided for {recipe!r} recipe:"
                        f" '{', '.join(set(inputs.keys()) - set(recipe_inputs.keys()))}'"
                    ),
                    style="red",
                )
            elif set(recipe_inputs.keys()) > set(inputs.keys()):
                table = Table(
                    title=f"[red]Required inputs for {recipe!r} recipe[/red]",
                )
                table.add_column("Field Name", style="green", no_wrap=True)
                table.add_column(
                    "Description", justify="left", style="white", no_wrap=False
                )
                for field, description in recipe_inputs.items():
                    if field not in inputs:
                        table.add_row(field, description)

                app.console.print(table)

                for key, description in recipe_inputs.items():
                    if key not in inputs:
                        inputs[key] = typer.prompt(key)

            app.console.print("-" * 15)

    try:
        files = [
            f"[green]{fname}[/green]"
            for fname in initialize_project(name=name, recipe=recipe, inputs=inputs)
        ]
    except ValueError as exc:
        if "Unknown recipe" in str(exc):
            exit_with_error(
                f"Unknown recipe {recipe!r} provided - run [yellow]`syncmatrix init"
                "`[/yellow] to see all available recipes."
            )
        else:
            raise

    files = "\n".join(files)
    empty_msg = (
        f"Created project in [green]{Path('.').resolve()}[/green]; no new files"
        " created."
    )
    file_msg = (
        f"Created project in [green]{Path('.').resolve()}[/green] with the following"
        f" new files:\n{files}"
    )
    app.console.print(file_msg if files else empty_msg)


@project_app.command()
async def clone(
    deployment_name: str = typer.Option(
        None,
        "--deployment",
        "-d",
        help="The name of the deployment to clone a project for.",
    ),
    deployment_id: str = typer.Option(
        None,
        "--id",
        "-i",
        help="The id of the deployment to clone a project for.",
    ),
):
    """
    Clone an existing project for a given deployment.
    """
    app.console.print(
        generate_deprecation_message(
            "The `syncmatrix project clone` command",
            start_date="Jun 2023",
        )
    )
    if deployment_name and deployment_id:
        exit_with_error(
            "Can only pass one of deployment name or deployment ID options."
        )

    if not deployment_name and not deployment_id:
        exit_with_error("Must pass either a deployment name or deployment ID.")

    if deployment_name:
        async with get_client() as client:
            try:
                deployment = await client.read_deployment_by_name(deployment_name)
            except ObjectNotFound:
                exit_with_error(f"Deployment {deployment_name!r} not found!")
    else:
        async with get_client() as client:
            try:
                deployment = await client.read_deployment(deployment_id)
            except ObjectNotFound:
                exit_with_error(f"Deployment {deployment_id!r} not found!")

    if deployment.pull_steps:
        output = await run_steps(deployment.pull_steps)
        app.console.out(output["directory"])
    else:
        exit_with_error("No pull steps found, exiting early.")


@project_app.command()
async def register_flow(
    entrypoint: str = typer.Argument(
        ...,
        help=(
            "The path to a flow entrypoint, in the form of"
            " `./path/to/file.py:flow_func_name`"
        ),
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help=(
            "An optional flag to force register this flow and overwrite any existing"
            " entry"
        ),
    ),
):
    """
    Register a flow with this project.
    """
    try:
        flow = await register(entrypoint, force=force)
    except Exception as exc:
        exit_with_error(exc)

    app.console.print(
        (
            f"Registered flow {flow.name!r} in"
            f" {(find_syncmatrix_directory()/'flows.json').resolve()!s}"
        ),
        style="green",
    )
