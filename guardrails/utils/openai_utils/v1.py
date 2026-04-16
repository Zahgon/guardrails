import os
from typing import Any, Dict, Iterator, List, Optional, cast

import openai

from guardrails.classes.llm.llm_response import LLMResponse
from guardrails.utils.safe_get import safe_get
from guardrails.telemetry import trace_llm_call, trace_operation


class OpenAIClientV1:
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        *args,
        **kwargs,
    ):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        self.api_key = api_key
        self.api_base = api_base
        self.client = openai.Client(
            api_key=self.api_key,
            base_url=self.api_base,
        )

    def create_embedding(
        self,
        model: str,
        input: List[str],
    ) -> List[List[float]]:
        embeddings = self.client.embeddings.create(
            model=model,
            input=input,
        )
        return [r.embedding for r in embeddings.data]

    def create_completion(
        self, engine: str, prompt: str, *args, **kwargs
    ) -> LLMResponse:
        pass

    def construct_nonchat_response(
        self,
        stream: bool,
        openai_response: Any,
    ) -> LLMResponse:
        """Construct an LLMResponse from an OpenAI response.

        Splits execution based on whether the `stream` parameter is set
        in the kwargs.
        """
        pass

    def create_chat_completion(
        self, model: str, messages: List[Any], *args, **kwargs
    ) -> LLMResponse:
        pass

    def construct_chat_response(
        self,
        stream: bool,
        openai_response: Any,
    ) -> LLMResponse:
        """Construct an LLMResponse from an OpenAI response.

        Splits execution based on whether the `stream` parameter is set
        in the kwargs.
        """
        pass
