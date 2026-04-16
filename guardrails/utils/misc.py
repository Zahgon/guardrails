import os
import random
from typing import List

from lxml.etree import Element as E
from rich.pretty import pretty_repr

from guardrails.classes.history.call import Call
from guardrails.actions.reask import gather_reasks
from guardrails.types import RailTypes


def generate_test_artifacts(
    rail_spec: str, call_log: Call, on_fail_type: str, artifact_dir: str
) -> None:
    """Generate artifacts for testing.

    Artifacts include: rail_spec, compiled_prompt, llm_output, validated_response.
    The artifacts are saved by on_fail_type. Check out
    tests/integration_tests/test_assets/entity_extraction/ for examples.

    This function is only intended to be used to create artifacts for integration tests
    once the call log (Call) object has been manually checked to be correct.

    Args:
        rail_spec: This should be a string representation of the rail.
        guard_history: The guard history object.
        on_fail_type: The type of action to take when a validator fails.
        artifact_dir: The artifact dir where the artifacts will be saved.
    """
    pass


def generate_random_schemas(n: int, depth: int = 4, width: int = 10) -> List[str]:
    """Generate random schemas that represent a valid schema.

    Args:
        n: The number of schemas to generate.
        depth: The depth of nesting
    """
    pass
