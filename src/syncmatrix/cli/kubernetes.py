"""
Command line interface for working with Syncmatrix on Kubernetes
"""
from string import Template

import typer
import yaml

import syncmatrix
from syncmatrix.cli._types import SyncmatrixTyper, SettingsOption
from syncmatrix.cli.root import app
from syncmatrix.infrastructure import KubernetesJob
from syncmatrix.settings import (
    SYNCMATRIX_API_KEY,
    SYNCMATRIX_API_URL,
    SYNCMATRIX_LOGGING_SERVER_LEVEL,
)
from syncmatrix.utilities.dockerutils import get_syncmatrix_image_name

kubernetes_app = SyncmatrixTyper(
    name="kubernetes",
    help="Commands for working with Syncmatrix on Kubernetes.",
)
app.add_typer(kubernetes_app)

manifest_app = SyncmatrixTyper(
    name="manifest",
    help="Commands for generating Kubernetes manifests.",
)
kubernetes_app.add_typer(manifest_app)


@manifest_app.command("server")
def manifest_server(
    image_tag: str = typer.Option(
        get_syncmatrix_image_name(),
        "-i",
        "--image-tag",
        help="The tag of a Docker image to use for the server.",
    ),
    namespace: str = typer.Option(
        "default",
        "-n",
        "--namespace",
        help="A Kubernetes namespace to create the server in.",
    ),
    log_level: str = SettingsOption(SYNCMATRIX_LOGGING_SERVER_LEVEL),
):
    """
    Generates a manifest for deploying Syncmatrix on Kubernetes.

    Example:
        $ syncmatrix kubernetes manifest server | kubectl apply -f -
    """

    template = Template(
        (
            syncmatrix.__module_path__ / "cli" / "templates" / "kubernetes-server.yaml"
        ).read_text()
    )
    manifest = template.substitute(
        {
            "image_name": image_tag,
            "namespace": namespace,
            "log_level": log_level,
        }
    )
    print(manifest)


@manifest_app.command("agent")
def manifest_agent(
    api_url: str = SettingsOption(SYNCMATRIX_API_URL),
    api_key: str = SettingsOption(SYNCMATRIX_API_KEY),
    image_tag: str = typer.Option(
        get_syncmatrix_image_name(),
        "-i",
        "--image-tag",
        help="The tag of a Docker image to use for the Agent.",
    ),
    namespace: str = typer.Option(
        "default",
        "-n",
        "--namespace",
        help="A Kubernetes namespace to create agent in.",
    ),
    work_queue: str = typer.Option(
        "kubernetes",
        "-q",
        "--work-queue",
        help="A work queue name for the agent to pull from.",
    ),
):
    """
    Generates a manifest for deploying Agent on Kubernetes.

    Example:
        $ syncmatrix kubernetes manifest agent | kubectl apply -f -
    """

    template = Template(
        (
            syncmatrix.__module_path__ / "cli" / "templates" / "kubernetes-agent.yaml"
        ).read_text()
    )
    manifest = template.substitute(
        {
            "api_url": api_url,
            "api_key": api_key,
            "image_name": image_tag,
            "namespace": namespace,
            "work_queue": work_queue,
        }
    )
    print(manifest)


@manifest_app.command("flow-run-job")
async def manifest_flow_run_job():
    """
    Prints the default KubernetesJob Job manifest.

    Use this file to fully customize your `KubernetesJob` deployments.

    \b
    Example:
        \b
        $ syncmatrix kubernetes manifest flow-run-job

    \b
    Output, a YAML file:
        \b
        apiVersion: batch/v1
        kind: Job
        ...
    """

    KubernetesJob.base_job_manifest()

    output = yaml.dump(KubernetesJob.base_job_manifest())

    # add some commentary where appropriate
    output = output.replace(
        "metadata:\n  labels:",
        "metadata:\n  # labels are required, even if empty\n  labels:",
    )
    output = output.replace(
        "containers:\n",
        "containers:  # the first container is required\n",
    )
    output = output.replace(
        "env: []\n",
        "env: []  # env is required, even if empty\n",
    )

    print(output)
