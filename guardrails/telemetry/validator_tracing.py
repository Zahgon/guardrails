from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
)

from opentelemetry import context, trace
from opentelemetry.trace import StatusCode, Tracer, Span

try:
    from openinference.semconv.trace import SpanAttributes  # type: ignore
except ImportError:
    SpanAttributes = None

from guardrails_ai.types import ValidationResult

from guardrails.settings import settings
from guardrails.telemetry.common import add_user_attributes, serialize
from guardrails.telemetry.open_inference import trace_operation
from guardrails.utils.casting_utils import to_string
from guardrails.utils.safe_get import safe_get
from guardrails.version import GUARDRAILS_VERSION


def add_validator_attributes(
    *args,
    validator_span: Span,
    validator_name: str,
    obj_id: int,
    on_fail_descriptor: Optional[str] = None,
    result: Optional[ValidationResult] = None,
    init_kwargs: Dict[str, Any] = {},
    validation_session_id: str,
    **kwargs,
):
    value_arg = serialize(safe_get(args, 0)) or ""
    metadata_arg = serialize(safe_get(args, 1, {})) or "{}"

    # Legacy Span Attributes
    validator_span.set_attribute("on_fail_descriptor", on_fail_descriptor or "noop")
    validator_span.set_attribute(
        "args",
        to_string({k: to_string(v) for k, v in init_kwargs.items()}) or "{}",
    )
    validator_span.set_attribute("instance_id", serialize(obj_id) or "")
    validator_span.set_attribute("input", value_arg)

    # New Span Attributes
    validator_span.set_attribute("type", "guardrails/guard/step/validator")
    validator_span.set_attribute("validation_session_id", validation_session_id)

    ### Validator.__init__ ###
    validator_span.set_attribute("validator.name", validator_name or "unknown")
    validator_span.set_attribute("validator.on_fail", on_fail_descriptor or "noop")
    validator_span.set_attribute("validator.instance_id", serialize(obj_id) or "")
    for k, v in init_kwargs.items():
        if v is not None:
            validator_span.set_attribute(f"validator.init.{k}", serialize(v) or "")

    ### Validator.validate ###
    validator_span.set_attribute("validator.validate.input.value", value_arg)
    validator_span.set_attribute("validator.validate.input.metadata", metadata_arg)
    for k, v in kwargs.items():
        if v is not None:
            validator_span.set_attribute(
                f"validator.validate.input.{k}", serialize(v) or ""
            )
    trace_operation(
        input_value={"value": value_arg, "metadata": metadata_arg},
        input_mime_type="application/json",
    )

    if result is not None:
        output = result.model_dump()
        trace_operation(
            output_value=output,
            output_mime_type="application/json",
        )
        for k, v in output.items():
            if v is not None:
                validator_span.set_attribute(
                    f"validator.validate.output.{k}", serialize(v) or ""
                )


def trace_validator(
    validator_name: str,
    obj_id: int,
    on_fail_descriptor: Optional[str] = None,
    tracer: Optional[Tracer] = None,
    *,
    validation_session_id: str,
    **init_kwargs,
):
    def trace_validator_decorator(fn: Callable[..., Optional[ValidationResult]]):
        @wraps(fn)
        pass

    return trace_validator_decorator


def trace_async_validator(
    validator_name: str,
    obj_id: int,
    on_fail_descriptor: Optional[str] = None,
    tracer: Optional[Tracer] = None,
    *,
    validation_session_id: str,
    **init_kwargs,
):
    def trace_validator_decorator(
        fn: Callable[..., Awaitable[Optional[ValidationResult]]],
    ):
        @wraps(fn)
        pass

    return trace_validator_decorator
