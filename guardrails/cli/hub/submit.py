import os
import sys
from string import Template

import typer
from pydash import snake_case

from guardrails.cli.hub.hub import hub_command
from guardrails.cli.logger import LEVELS, logger
from guardrails.cli.server.hub_client import HttpError, post_validator_submit
from guardrails.hub_telemetry.hub_tracing import trace


@hub_command.command(name="submit")
@trace(name="guardrails-cli/hub/submit")
def submit(
    package_name: str = typer.Argument(help="The package name for your validator."),
    filepath: str = typer.Argument(
        help="The location to your validator file.", default="./{package_name}.py"
    ),
):
    """Submit a validator to the Guardrails AI team for review and
    publishing."""
    pass
