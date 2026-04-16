from contextvars import ContextVar, copy_context
import sys
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    cast,
)

from guardrails.validator_service import AsyncValidatorService
from guardrails.actions.reask import SkeletonReAsk
from guardrails.classes import ValidationOutcome
from guardrails.classes.history import Call, Inputs, Iteration, Outputs
from guardrails.classes.output_type import OutputTypes
from guardrails.llm_providers import (
    AsyncPromptCallableBase,
)
from guardrails.logger import set_scope
from guardrails.run import StreamRunner
from guardrails.run.async_runner import AsyncRunner
from guardrails.telemetry import trace_async_stream_step
from guardrails.hub_telemetry.hub_tracing import async_trace_stream
from guardrails.types import OnFailAction
from guardrails_ai.types import (
    PassResult,
    FailResult,
)


if sys.version_info.minor < 10:
    from guardrails.utils.polyfills import anext


class AsyncStreamRunner(AsyncRunner, StreamRunner):
    # @async_trace_stream(name="/reasks", origin="AsyncStreamRunner.async_run")
    async def async_run(
        self, call_log: Call, prompt_params: Optional[Dict] = None
    ) -> AsyncIterator[ValidationOutcome]:
        pass

    @async_trace_stream(name="/step", origin="AsyncStreamRunner.async_step")
    @trace_async_stream_step
    async def async_step(
        self,
        index: int,
        output_schema: Dict[str, Any],
        call_log: Call,
        *,
        api: Optional[AsyncPromptCallableBase],
        messages: Optional[List[Dict]] = None,
        prompt_params: Optional[Dict] = None,
        output: Optional[str] = None,
    ) -> AsyncIterator[ValidationOutcome]:
        pass
