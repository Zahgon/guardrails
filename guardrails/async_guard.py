from builtins import id as object_id
import contextvars
import inspect
from opentelemetry import context as otel_context
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    Union,
    cast,
)

from guardrails_ai.types import (
    ValidationOutcome as IValidationOutcome,
)

from guardrails import Guard
from guardrails.classes import OT, ValidationOutcome
from guardrails.classes.history import Call
from guardrails.classes.history.call_inputs import CallInputs
from guardrails.classes.output_type import OutputTypes
from guardrails.classes.schema.processed_schema import ProcessedSchema
from guardrails.formatters.base_formatter import BaseFormatter
from guardrails.llm_providers import get_async_llm_ask, model_is_supported_server_side
from guardrails.logger import set_scope
from guardrails.run import AsyncRunner, AsyncStreamRunner
from guardrails.stores.context import get_call_kwarg, set_call_kwargs
from guardrails.hub_telemetry.hub_tracing import async_trace
from guardrails.types.pydantic import ModelOrListOfModels
from guardrails.telemetry import trace_async_guard_execution, wrap_with_otel_context
from guardrails.utils.validator_utils import verify_metadata_requirements
from guardrails.validator_base import Validator


class AsyncGuard(Guard, Generic[OT]):
    """The AsyncGuard class.

    This class one of the main entry point for using Guardrails. It is
    initialized from one of the following class methods:

    - `for_rail`
    - `for_rail_string`
    - `for_pydantic`
    - `for_string`

    The `__call__`
    method functions as a wrapper around LLM APIs. It takes in an Async LLM
    API, and optional prompt parameters, and returns the raw output stream from
    the LLM and the validated output stream.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def _for_rail_schema(
        cls,
        schema: ProcessedSchema,
        rail: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        guard = super()._for_rail_schema(
            schema,
            rail,
            name=name,
            description=description,
        )
        if schema.output_type == OutputTypes.STRING:
            return cast(AsyncGuard[str], guard)
        elif schema.output_type == OutputTypes.LIST:
            return cast(AsyncGuard[List], guard)
        else:
            return cast(AsyncGuard[Dict], guard)

    @classmethod
    def for_pydantic(
        cls,
        output_class: ModelOrListOfModels,
        *,
        messages: Optional[List[Dict]] = None,
        reask_messages: Optional[List[Dict]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        output_formatter: Optional[Union[str, BaseFormatter]] = None,
    ):
        guard = super().for_pydantic(
            output_class,
            messages=messages,
            reask_messages=reask_messages,
            name=name,
            description=description,
            output_formatter=output_formatter,
        )
        if guard._output_type == OutputTypes.LIST:
            return cast(AsyncGuard[List], guard)
        else:
            return cast(AsyncGuard[Dict], guard)

    @classmethod
    def for_string(
        cls,
        validators: Sequence[Validator],
        *,
        string_description: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        reask_messages: Optional[List[Dict]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        guard = super().for_string(
            validators,
            string_description=string_description,
            messages=messages,
            reask_messages=reask_messages,
            name=name,
            description=description,
        )
        return cast(AsyncGuard[str], guard)

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional["AsyncGuard"]:
        guard = super().from_dict(obj)
        return cast(AsyncGuard, guard)

    def use(
        self,
        *validator_spread: Validator,
        validators: List[Validator] = [],
        on: str = "output",
    ) -> "AsyncGuard":
        pass

    async def _execute(
        self,
        *args,
        llm_api: Optional[Callable[..., Awaitable[Any]]] = None,
        llm_output: Optional[str] = None,
        prompt_params: Optional[Dict] = None,
        num_reasks: Optional[int] = None,
        messages: Optional[List[Dict]] = None,
        metadata: Optional[Dict],
        full_schema_reask: Optional[bool] = None,
        **kwargs,
    ) -> Union[
        ValidationOutcome[OT],
        Awaitable[ValidationOutcome[OT]],
        AsyncIterator[ValidationOutcome[OT]],
    ]:
        pass

    async def _exec(
        self,
        *args,
        llm_api: Optional[Callable[[Any], Awaitable[Any]]],
        llm_output: Optional[str] = None,
        call_log: Call,
        prompt_params: Dict,  # Should be defined at this point
        num_reasks: int = 0,  # Should be defined at this point
        metadata: Dict,  # Should be defined at this point
        full_schema_reask: bool = False,  # Should be defined at this point
        messages: Optional[List[Dict]],
        **kwargs,
    ) -> Union[
        ValidationOutcome[OT],
        Awaitable[ValidationOutcome[OT]],
        AsyncIterator[ValidationOutcome[OT]],
    ]:
        """Call the LLM asynchronously and validate the output.

        Args:
            llm_api: The LLM API to call asynchronously (e.g. openai.Completion.acreate)
            prompt_params: The parameters to pass to the prompt.format() method.
            num_reasks: The max times to re-ask the LLM for invalid output.
            messages: The message history to pass to the LLM.
            metadata: Metadata to pass to the validators.
            full_schema_reask: When reasking, whether to regenerate the full schema
                               or just the incorrect values.
                               Defaults to `True` if a base model is provided,
                               `False` otherwise.

        Returns:
            The raw text output from the LLM and the validated output.
        """
        pass

    @async_trace(name="/guard_call", origin="AsyncGuard.__call__")
    async def __call__(
        self,
        llm_api: Optional[Callable[..., Awaitable[Any]]] = None,
        *args,
        prompt_params: Optional[Dict] = None,
        num_reasks: Optional[int] = 1,
        messages: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None,
        full_schema_reask: Optional[bool] = None,
        **kwargs,
    ) -> Union[
        ValidationOutcome[OT],
        Awaitable[ValidationOutcome[OT]],
        AsyncIterator[ValidationOutcome[OT]],
    ]:
        """Call the LLM and validate the output. Pass an async LLM API to
        return a coroutine.

        Args:
            llm_api: The LLM API to call
                     (e.g. openai.completions.create or openai.chat.completions.create)
            prompt_params: The parameters to pass to the prompt.format() method.
            num_reasks: The max times to re-ask the LLM for invalid output.
            messages: The message history to pass to the LLM.
            metadata: Metadata to pass to the validators.
            full_schema_reask: When reasking, whether to regenerate the full schema
                               or just the incorrect values.
                               Defaults to `True` if a base model is provided,
                               `False` otherwise.

        Returns:
            The raw text output from the LLM and the validated output.
        """

        # Retrieve messages from the provided arguments or default options
        messages_from_kwargs = kwargs.pop("messages", None)
        messages_from_exec_opts = self._exec_opts.messages

        # Determine the final value for messages
        messages = messages or messages_from_kwargs or messages_from_exec_opts or []

        if messages is not None and not len(messages):
            raise RuntimeError(
                "You must provide a prompt if messages is empty. "
                "Alternatively, you can provide a prompt in the Schema constructor."
            )

        return await trace_async_guard_execution(
            self.name,
            self.history,
            self._execute,
            *args,
            llm_api=llm_api,
            prompt_params=prompt_params,
            num_reasks=num_reasks,
            messages=messages,
            metadata=metadata,
            full_schema_reask=full_schema_reask,
            **kwargs,
        )

    @async_trace(name="/guard_call", origin="AsyncGuard.parse")
    async def parse(
        self,
        llm_output: str,
        *args,
        metadata: Optional[Dict] = None,
        llm_api: Optional[Callable[..., Awaitable[Any]]] = None,
        num_reasks: Optional[int] = None,
        prompt_params: Optional[Dict] = None,
        full_schema_reask: Optional[bool] = None,
        **kwargs,
    ) -> Awaitable[ValidationOutcome[OT]]:
        """Alternate flow to using AsyncGuard where the llm_output is known.

        Args:
            llm_output: The output being parsed and validated.
            metadata: Metadata to pass to the validators.
            llm_api: The LLM API to call
                     (e.g. openai.completions.create or openai.Completion.acreate)
            num_reasks: The max times to re-ask the LLM for invalid output.
            prompt_params: The parameters to pass to the prompt.format() method.
            full_schema_reask: When reasking, whether to regenerate the full schema
                               or just the incorrect values.

        Returns:
            The validated response. This is either a string or a dictionary,
                determined by the object schema defined in the RAILspec.
        """

        final_num_reasks = (
            num_reasks
            if num_reasks is not None
            else self._num_reasks
            if self._num_reasks is not None
            else 0
            if llm_api is None
            else 1
        )
        default_messages = self._exec_opts.messages if llm_api else None
        messages = kwargs.pop("messages", default_messages)

        return await trace_async_guard_execution(  # type: ignore
            self.name,
            self.history,
            self._execute,
            *args,
            llm_output=llm_output,
            llm_api=llm_api,
            prompt_params=prompt_params,
            num_reasks=final_num_reasks,
            messages=messages,
            metadata=metadata,
            full_schema_reask=full_schema_reask,
            **kwargs,
        )

    async def _stream_server_call(
        self, *, payload: Dict[str, Any]
    ) -> AsyncIterator[ValidationOutcome[OT]]:
        # TODO: Once server side supports async streaming, this function will need to
        # yield async generators, not generators
        pass

    @async_trace(name="/guard_call", origin="AsyncGuard.validate")
    async def validate(
        self, llm_output: str, *args, **kwargs
    ) -> Awaitable[ValidationOutcome[OT]]:
        return await self.parse(llm_output=llm_output, *args, **kwargs)

    @classmethod
    def load(
        cls,
        name: str,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        history_max_length: Optional[int] = None,
    ) -> Optional["AsyncGuard"]:
        guard = super().load(
            name,
            api_key=api_key,
            base_url=base_url,
            history_max_length=history_max_length,
        )
        if guard:
            return cast(AsyncGuard, guard)
