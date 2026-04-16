from guardrails.cli.hub.hub import hub_command
from guardrails.hub.registry import get_registry
from guardrails.hub_telemetry.hub_tracing import trace
from .console import console


@hub_command.command(name="list")
@trace(name="guardrails-cli/hub/list")
def list():
    """List all installed validators."""
    pass
