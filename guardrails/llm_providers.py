import asyncio

import inspect
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Union,
    cast,
)

from guardrails.prompt import Prompt, Instructions

from guardrails.errors import UserFacingException
from guardrails.classes.llm.llm_response import LLMResponse
from guardrails.classes.llm.prompt_callable import (
    CALLABLE_FAILURE_SUFFIX,
    PromptCallableBase,
    PromptCallableException,
)

from guardrails.types.inputs import MessageHistory

import warnings

from guardrails.utils.safe_get import safe_get
from guardrails.telemetry import trace_llm_call, trace_operation

from guardrails.utils.prompt_utils import messages_to_prompt_string

###
# Synchronous wrappers
###


def nonchat_prompt(prompt: str, instructions: Optional[str] = None) -> str:
    """Prepare final prompt for nonchat engine."""
    pass


def chat_prompt(
    prompt: Optional[str],
    instructions: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
) -> List[Dict[str, str]]:
    """Prepare final prompt for chat engine."""
    if messages:
        return messages
    if prompt is None:
        raise PromptCallableException(
            "You must pass in either `text` or `messages` to `guard.__call__`."
        )

    if not instructions:
        instructions = "You are a helpful assistant."

    return [
        {"role": "system", "content": instructions},
        {"role": "user", "content": prompt},
    ]


def litellm_messages(
    prompt: Optional[str],
    instructions: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
) -> List[Dict[str, str]]:
    """Prepare messages for LiteLLM."""
    pass


class ManifestCallable(PromptCallableBase):
    def _invoke_llm(
        self,
        text: str,
        client: Any,
        instructions: Optional[str] = None,
        *args,
        **kwargs,
    ) -> LLMResponse:
        """Wrapper for manifest client.

        To use manifest for guardrailse, do
        ```
        client = Manifest(client_name=..., client_connection=...)
        raw_llm_response, validated_response, *rest = guard(
            client,
            prompt_params={...},
            ...
        ```
        """
        pass


class LiteLLMCallable(PromptCallableBase):
    def _invoke_llm(
        self,
        text: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        messages: Optional[List[Dict]] = None,
        *args,
        **kwargs,
    ) -> LLMResponse:
        """Wrapper for Lite LLM completions.

        To use Lite LLM for guardrails, do
        ```
        from litellm import completion

        raw_llm_response, validated_response = guard(
            completion,
            model="gpt-3.5-turbo",
            prompt_params={...},
            temperature=...,
            ...
        )
        ```
        """
        pass


class HuggingFaceModelCallable(PromptCallableBase):
    def _invoke_llm(
        self,
        model_generate: Any,
        *args,
        messages: Union[
            list[dict[str, Union[str, Prompt, Instructions]]], MessageHistory
        ],
        **kwargs,
    ) -> LLMResponse:
        pass


class HuggingFacePipelineCallable(PromptCallableBase):
    def _invoke_llm(
        self,
        pipeline: Any,
        *args,
        messages: Union[
            list[dict[str, Union[str, Prompt, Instructions]]], MessageHistory
        ],
        **kwargs,
    ) -> LLMResponse:
        pass


class ArbitraryCallable(PromptCallableBase):
    def __init__(self, llm_api: Optional[Callable] = None, *args, **kwargs):
        llm_api_args = inspect.getfullargspec(llm_api)
        if not llm_api_args.varkw:
            raise ValueError("Custom LLM callables must accept **kwargs!")
        if not llm_api_args.kwonlyargs or "messages" not in llm_api_args.kwonlyargs:
            warnings.warn(
                "We recommend including 'messages'"
                " as keyword-only arguments for custom LLM callables."
                " Doing so ensures these arguments are not unintentionally"
                " passed through to other calls via **kwargs.",
                UserWarning,
            )
        self.llm_api = llm_api
        super().__init__(*args, **kwargs)

    def _invoke_llm(self, *args, **kwargs) -> LLMResponse:
        """Wrapper for arbitrary callable.

        To use an arbitrary callable for guardrails, do
        ```
        raw_llm_response, validated_response, *rest = guard(
            my_callable,
            prompt_params={...},
            ...
        )
        ```
        """
        pass


def get_llm_ask(
    llm_api: Optional[Callable] = None,
    *args,
    **kwargs,
) -> Optional[PromptCallableBase]:
    if "temperature" not in kwargs:
        model = kwargs.get("model", "")
        if not (
            isinstance(model, str)
            and (model.startswith("gpt-5") or model.startswith("openai/gpt-5"))
        ):
            warnings.warn(
                "The default value of 0 for temperature is deprecated "
                "and will be removed in guardrails-ai v0.8.x and higher.",
                DeprecationWarning,
            )
            kwargs.update({"temperature": 0})

    try:
        from litellm import completion

        if llm_api == completion or (llm_api is None and kwargs.get("model")):
            return LiteLLMCallable(*args, **kwargs)
    except ImportError:
        pass

    if llm_api is not None:
        llm_self = getattr(llm_api, "__self__", None)
        if (
            llm_self is not None
            and hasattr(llm_self, "__class__")
            and getattr(llm_self.__class__, "__name__", None) == "GuardrailsEngine"
            and getattr(llm_api, "__name__", None) == "engine_api"
        ):
            return ArbitraryCallable(*args, llm_api=llm_api, **kwargs)

    try:
        import manifest  # noqa: F401 # type: ignore

        if isinstance(llm_api, manifest.Manifest):
            return ManifestCallable(*args, client=llm_api, **kwargs)
    except ImportError:
        pass

    try:
        from transformers import (  # noqa: F401 # type: ignore
            FlaxPreTrainedModel,
            GenerationMixin,
            PreTrainedModel,
            TFPreTrainedModel,
        )

        api_self = getattr(llm_api, "__self__", None)

        if (
            isinstance(api_self, PreTrainedModel)
            or isinstance(api_self, TFPreTrainedModel)
            or isinstance(api_self, FlaxPreTrainedModel)
        ):
            if (
                hasattr(llm_api, "__func__")
                and llm_api.__func__ == GenerationMixin.generate  # type: ignore
            ):
                return HuggingFaceModelCallable(*args, model_generate=llm_api, **kwargs)
            raise ValueError("Only text generation models are supported at this time.")
    except ImportError:
        pass

    try:
        from transformers import Pipeline  # noqa: F401 # type: ignore

        if isinstance(llm_api, Pipeline):
            # Couldn't find a constant for this
            if llm_api.task == "text-generation":
                return HuggingFacePipelineCallable(*args, pipeline=llm_api, **kwargs)
            raise ValueError(
                "Only text generation pipelines are supported at this time."
            )
    except ImportError:
        pass

    # Let the user pass in an arbitrary callable.
    if llm_api is not None:
        return ArbitraryCallable(*args, llm_api=llm_api, **kwargs)


###
# Async wrappers
###


class AsyncPromptCallableBase(PromptCallableBase):
    async def invoke_llm(
        self,
        *args,
        **kwargs,
    ) -> LLMResponse:
        raise NotImplementedError

    async def __call__(self, *args, **kwargs) -> LLMResponse:
        try:
            result = await self.invoke_llm(
                *self.init_args, *args, **self.init_kwargs, **kwargs
            )
        except Exception as e:
            raise PromptCallableException(
                "The callable `fn` passed to `Guard(fn, ...)` failed"
                f" with the following error: `{e}`. {CALLABLE_FAILURE_SUFFIX}"
            )
        if not isinstance(result, LLMResponse):
            raise PromptCallableException(
                "The callable `fn` passed to `Guard(fn, ...)` returned"
                f" a non-string value: {result}. {CALLABLE_FAILURE_SUFFIX}"
            )
        return result


class AsyncLiteLLMCallable(AsyncPromptCallableBase):
    async def invoke_llm(
        self,
        text: Optional[str] = None,
        instructions: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        *args,
        **kwargs,
    ):
        """Wrapper for Lite LLM completions.

        To use Lite LLM for guardrails, do
        ```
        from litellm import completion

        raw_llm_response, validated_response = guard(
            completion,
            model="gpt-3.5-turbo",
            prompt_params={...},
            temperature=...,
            ...
        )
        ```
        """
        pass


class AsyncManifestCallable(AsyncPromptCallableBase):
    async def invoke_llm(
        self,
        text: str,
        client: Any,
        instructions: Optional[str] = None,
        *args,
        **kwargs,
    ):
        """Async wrapper for manifest client.

        To use manifest for guardrails, do
        ```
        client = Manifest(client_name=..., client_connection=...)
        raw_llm_response, validated_response, *rest = guard(
            client,
            prompt_params={...},
            ...
        ```
        """
        pass


class AsyncArbitraryCallable(AsyncPromptCallableBase):
    def __init__(self, llm_api: Callable, *args, **kwargs):
        llm_api_args = inspect.getfullargspec(llm_api)
        if not llm_api_args.varkw:
            raise ValueError("Custom LLM callables must accept **kwargs!")
        if not llm_api_args.kwonlyargs or "messages" not in llm_api_args.kwonlyargs:
            warnings.warn(
                "We recommend including 'messages'"
                " as keyword-only arguments for custom LLM callables."
                " Doing so ensures these arguments are not unintentionally"
                " passed through to other calls via **kwargs.",
                UserWarning,
            )
        self.llm_api = llm_api
        super().__init__(*args, **kwargs)

    async def invoke_llm(self, *args, **kwargs) -> LLMResponse:
        """Wrapper for arbitrary callable.

        To use an arbitrary callable for guardrails, do
        ```
        raw_llm_response, validated_response, *rest = guard(
            my_callable,
            prompt_params={...},
            ...
        )
        ```
        """
        pass


def get_async_llm_ask(
    llm_api: Callable[..., Awaitable[Any]], *args, **kwargs
) -> AsyncPromptCallableBase:
    try:
        import litellm

        if llm_api == litellm.acompletion or (llm_api is None and kwargs.get("model")):
            return AsyncLiteLLMCallable(*args, **kwargs)
    except ImportError:
        pass

    try:
        import manifest  # noqa: F401 # type: ignore

        if isinstance(llm_api, manifest.Manifest):
            return AsyncManifestCallable(*args, client=llm_api, **kwargs)
    except ImportError:
        pass

    if llm_api is not None:
        return AsyncArbitraryCallable(*args, llm_api=llm_api, **kwargs)


def model_is_supported_server_side(
    llm_api: Optional[Union[Callable, Callable[..., Awaitable[Any]]]] = None,
    *args,
    **kwargs,
) -> bool:
    if not llm_api:
        return True
    # TODO: Support other models; requires server-side updates
    model = get_llm_ask(llm_api, *args, **kwargs)
    if asyncio.iscoroutinefunction(llm_api):
        model = get_async_llm_ask(llm_api, *args, **kwargs)
    return isinstance(model, LiteLLMCallable) or isinstance(model, AsyncLiteLLMCallable)
