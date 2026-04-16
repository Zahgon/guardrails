import typer
from importlib.metadata import version

from guardrails.cli.guardrails import guardrails
from guardrails.cli.hub.utils import installer_process
from guardrails.cli.logger import logger
from guardrails.cli.telemetry import trace_if_enabled
from guardrails.cli.version import version_warnings_if_applicable
from guardrails.cli.hub.console import console
from guardrails.settings import settings


def api_is_installed() -> bool:
    pass


@guardrails.command()
def start(
    env: str = typer.Option(
        default="",
        help="An env file to load environment variables from.",
    ),
    config: str = typer.Option(
        default="",
        help="A config file to load Guards from.",
    ),
    port: int = typer.Option(
        default=8000,
        help="The port to run the server on.",
    ),
    watch: bool = typer.Option(
        default=False, is_flag=True, help="Enable watch mode for logs."
    ),
    env_override: bool = typer.Option(
        default=False,
        help="Override existing environment variables with values from the env file.",
    ),
):
    pass
