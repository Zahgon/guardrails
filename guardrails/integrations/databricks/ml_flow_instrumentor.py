from functools import wraps
import inspect
import sys
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Iterator,
    Union,
)

from guardrails import Guard, AsyncGuard, settings
from guardrails_ai.types import ValidationResult
from guardrails.run import Runner, StreamRunner, AsyncRunner, AsyncStreamRunner
from guardrails.validator_base import Validator
from guardrails.version import GUARDRAILS_VERSION
from guardrails.telemetry.guard_tracing import (
    add_guard_attributes,
    trace_stream_guard,
    trace_async_stream_guard,
)
from guardrails.telemetry.runner_tracing import add_step_attributes, add_call_attributes
from guardrails.telemetry.validator_tracing import add_validator_attributes
from guardrails.classes.generic.stack import Stack
from guardrails.classes.llm.llm_response import LLMResponse
from guardrails.classes.history.iteration import Iteration
from guardrails.classes.output_type import OT
from guardrails.classes.validation_outcome import ValidationOutcome
from guardrails.utils.safe_get import safe_get

try:
    import mlflow
    import mlflow.tracing
    import mlflow.tracing.provider
    from mlflow.entities.span_status import SpanStatusCode
except ImportError:
    raise ImportError("Please install mlflow to use this instrumentor")


if sys.version_info.minor < 10:
    from guardrails.utils.polyfills import anext


# TODO: Abstract these methods and common logic into a base class
#   that can be extended by other instrumentors
class MlFlowInstrumentor:
    """Instruments Guardrails to send traces to MLFlow."""

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        # Disable legacy OTEL tracing to avoid duplicate spans
        settings.disable_tracing = True

    def instrument(self):
        pass

    def _instrument_guard(
        self,
        guard_execute: Callable[
            ..., Union[ValidationOutcome[OT], Iterator[ValidationOutcome[OT]]]
        ],
    ):
        @wraps(guard_execute)
        pass

    def _instrument_async_guard(
        self,
        guard_execute: Callable[
            ...,
            Coroutine[
                Any,
                Any,
                Union[
                    ValidationOutcome[OT],
                    Awaitable[ValidationOutcome[OT]],
                    AsyncIterator[ValidationOutcome[OT]],
                ],
            ],
        ],
    ):
        @wraps(guard_execute)
        pass

    def _instrument_runner_step(self, runner_step: Callable[..., Iteration]):
        @wraps(runner_step)
        pass

    def _instrument_stream_runner_step(
        self, runner_step: Callable[..., Iterator[ValidationOutcome[OT]]]
    ):
        @wraps(runner_step)
        pass

    def _instrument_async_runner_step(
        self, runner_step: Callable[..., Awaitable[Iteration]]
    ):
        @wraps(runner_step)
        pass

    def _instrument_async_stream_runner_step(
        self, runner_step: Callable[..., AsyncIterator[ValidationOutcome[OT]]]
    ) -> Callable[..., AsyncIterator[ValidationOutcome[OT]]]:
        @wraps(runner_step)
        pass

    def _instrument_runner_call(self, runner_call: Callable[..., LLMResponse]):
        @wraps(runner_call)
        pass

    def _instrument_async_runner_call(
        self, runner_call: Callable[..., Awaitable[LLMResponse]]
    ):
        @wraps(runner_call)
        pass

    def _instrument_validator_validate(
        self, validator_validate: Callable[..., ValidationResult]
    ):
        @wraps(validator_validate)
        pass

    def _instrument_validator_async_validate(
        self,
        validator_async_validate: Callable[..., Coroutine[Any, Any, ValidationResult]],
    ):
        @wraps(validator_async_validate)
        pass
