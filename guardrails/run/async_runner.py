import copy
from functools import partial
from typing import Any, Dict, List, Optional, cast


from guardrails import validator_service
from guardrails.classes.execution.guard_execution_options import GuardExecutionOptions
from guardrails.classes.history import Call, Inputs, Iteration, Outputs
from guardrails.classes.output_type import OutputTypes
from guardrails.errors import ValidationError
from guardrails.llm_providers import AsyncPromptCallableBase
from guardrails.logger import set_scope
from guardrails.run.runner import Runner
from guardrails.run.utils import messages_source
from guardrails.schema.validator import schema_validation
from guardrails.hub_telemetry.hub_tracing import async_trace
from guardrails.types.inputs import MessageHistory
from guardrails.types.pydantic import ModelOrListOfModels
from guardrails.types.validator import ValidatorMap
from guardrails.utils.exception_utils import UserFacingException
from guardrails.classes.llm.llm_response import LLMResponse
from guardrails.actions.reask import NonParseableReAsk, ReAsk
from guardrails.telemetry import trace_async_call, trace_async_step

from guardrails.constants import fail_status
from guardrails.prompt import Prompt


class AsyncRunner(Runner):
    def __init__(
        self,
        output_type: OutputTypes,
        output_schema: Dict[str, Any],
        num_reasks: int,
        validation_map: ValidatorMap,
        *,
        messages: Optional[List[Dict]] = None,
        api: Optional[AsyncPromptCallableBase] = None,
        metadata: Optional[Dict[str, Any]] = None,
        output: Optional[str] = None,
        base_model: Optional[ModelOrListOfModels] = None,
        full_schema_reask: bool = False,
        disable_tracer: Optional[bool] = True,
        exec_options: Optional[GuardExecutionOptions] = None,
    ):
        super().__init__(
            output_type=output_type,
            output_schema=output_schema,
            num_reasks=num_reasks,
            validation_map=validation_map,
            messages=messages,
            api=api,
            metadata=metadata,
            output=output,
            base_model=base_model,
            full_schema_reask=full_schema_reask,
            disable_tracer=disable_tracer,
            exec_options=exec_options,
        )
        self.api = api

    # TODO: Refactor this to use inheritance and overrides
    # Why are we using a different method here instead of just overriding?
    @async_trace(name="/reasks", origin="AsyncRunner.async_run")
    async def async_run(
        self, call_log: Call, prompt_params: Optional[Dict] = None
    ) -> Call:
        """Execute the runner by repeatedly calling step until the reask budget
        is exhausted.

        Args:
            prompt_params: Parameters to pass to the prompt in order to
                generate the prompt string.

        Returns:
            The Call log for this run.
        """
        pass

    # TODO: Refactor this to use inheritance and overrides
    @async_trace(name="/step", origin="AsyncRunner.async_step")
    @trace_async_step
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
    ) -> Iteration:
        """Run a full step."""
        pass

    # TODO: Refactor this to use inheritance and overrides
    @async_trace(name="/llm_call", origin="AsyncRunner.async_call")
    @trace_async_call
    async def async_call(
        self,
        messages: Optional[List[Dict]],
        api: Optional[AsyncPromptCallableBase],
        output: Optional[str] = None,
    ) -> LLMResponse:
        """Run a step.

        1. Query the LLM API,
        2. Convert the response string to a dict,
        3. Log the output
        """
        pass

    # TODO: Refactor this to use inheritance and overrides
    @async_trace(name="/validation", origin="AsyncRunner.async_validate")
    async def async_validate(
        self,
        iteration: Iteration,
        attempt_number: int,
        parsed_output: Any,
        output_schema: Dict[str, Any],
        stream: Optional[bool] = False,
        **kwargs,
    ):
        """Validate the output."""
        # Break early if empty
        if parsed_output is None:
            return None

        skeleton_reask = schema_validation(parsed_output, output_schema, **kwargs)
        if skeleton_reask:
            return skeleton_reask

        if self.output_type != OutputTypes.STRING:
            stream = None

        validated_output, metadata = await validator_service.async_validate(
            value=parsed_output,
            metadata=self.metadata,
            validator_map=self.validation_map,
            iteration=iteration,
            disable_tracer=self._disable_tracer,
            path="$",
            stream=stream,
            **kwargs,
        )
        self.metadata.update(metadata)
        validated_output = validator_service.post_process_validation(
            validated_output, attempt_number, iteration, self.output_type
        )

        return validated_output

    # TODO: Refactor this to use inheritance and overrides
    @async_trace(name="/input_prep", origin="AsyncRunner.async_prepare")
    async def async_prepare(
        self,
        call_log: Call,
        attempt_number: int,
        *,
        messages: Optional[List[Dict]],
        prompt_params: Optional[Dict] = None,
        api: Optional[AsyncPromptCallableBase],
    ) -> Optional[List[Dict]]:
        """Prepare by running pre-processing and input validation.

        Returns:
            The messages.
        """
        pass

    async def prepare_messages(
        self,
        call_log: Call,
        messages: MessageHistory,
        prompt_params: Dict,
        attempt_number: int,
    ) -> MessageHistory:
        pass

    @async_trace(name="/input_validation", origin="AsyncRunner.validate_messages")
    async def validate_messages(
        self, call_log: Call, messages: MessageHistory, attempt_number: int
    ):
        pass
