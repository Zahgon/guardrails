from typing import Any, Dict, Iterator, List, Optional, Tuple, Union, cast

from guardrails import validator_service
from guardrails.classes.history import Call, Inputs, Iteration, Outputs
from guardrails.classes.output_type import OT, OutputTypes
from guardrails.classes.validation_outcome import ValidationOutcome
from guardrails.llm_providers import (
    PromptCallableBase,
)
from guardrails.run.runner import Runner
from guardrails.hub_telemetry.hub_tracing import trace_stream
from guardrails.utils.parsing_utils import (
    coerce_types,
    parse_llm_output,
    prune_extra_keys,
)
from guardrails.actions.reask import ReAsk, SkeletonReAsk
from guardrails.constants import pass_status
from guardrails.telemetry import trace_stream_step
from guardrails.utils.safe_get import safe_get


class StreamRunner(Runner):
    """Runner class that calls a streaming LLM API with a prompt.

    This class performs output validation when the output is a stream of
    chunks. Inherits from Runner class, as overall structure remains
    similar.
    """

    @trace_stream(name="/reasks", origin="StreamRunner.__call__")
    def __call__(
        self, call_log: Call, prompt_params: Optional[Dict] = {}
    ) -> Iterator[ValidationOutcome[OT]]:
        """Execute the StreamRunner.

        Args:
            prompt_params: Parameters to pass to the prompt in order to
                generate the prompt string.

        Returns:
            The Call log for this run.
        """

        prompt_params = prompt_params or {}

        (
            messages,
            output_schema,
        ) = (
            self.messages,
            self.output_schema,
        )

        return self.step(
            index=0,
            api=self.api,
            messages=messages,
            prompt_params=prompt_params,
            output_schema=output_schema,
            output=self.output,
            call_log=call_log,
        )

    @trace_stream(name="/step", origin="StreamRunner.step")
    @trace_stream_step
    def step(
        self,
        index: int,
        api: Optional[PromptCallableBase],
        messages: Optional[List[Dict]],
        prompt_params: Dict,
        output_schema: Dict[str, Any],
        call_log: Call,
        output: Optional[str] = None,
    ) -> Iterator[ValidationOutcome[OT]]:
        """Run a full step."""
        pass

    def is_last_chunk(self, chunk: Any, api: Union[PromptCallableBase, None]) -> bool:
        """Detect if chunk is final chunk."""
        pass

    def get_chunk_text(self, chunk: Any, api: Union[PromptCallableBase, None]) -> str:
        """Get the text from a chunk.

        chunk is assumed to be an Iterator of either string or
        ChatCompletionChunk

        These types are not properly enforced upstream so we must use
        reflection
        """
        pass

    def parse(
        self, output: str, output_schema: Dict[str, Any], *, verified: set, **kwargs
    ):
        """Parse the output."""
        parsed_output, error = parse_llm_output(
            output, self.output_type, stream=True, verified=verified
        )

        if parsed_output and not error and not isinstance(parsed_output, ReAsk):
            parsed_output = prune_extra_keys(parsed_output, output_schema)
            parsed_output = coerce_types(parsed_output, output_schema)

        # Error can be either of
        # (True/False/None/ValueError/string representing error)
        if error:
            # If parsing error is a string,
            # it is an error from output_schema.parse_fragment()
            if isinstance(error, str):
                raise ValueError("Unable to parse output: " + error)
        # Else if either of
        # (None/True/False/ValueError), return parsed_output and error

        return parsed_output, error
