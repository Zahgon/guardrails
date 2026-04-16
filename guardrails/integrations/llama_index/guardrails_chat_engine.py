from typing import Any, Optional, Dict, List
from guardrails import Guard
from guardrails.errors import ValidationError


try:
    import llama_index  # noqa: F401
    from llama_index.core.chat_engine.types import (
        BaseChatEngine,
        AGENT_CHAT_RESPONSE_TYPE,
        AgentChatResponse,
        StreamingAgentChatResponse,
    )
    from llama_index.core.base.llms.types import ChatMessage
    from llama_index.core.prompts.mixin import PromptMixinType
except ImportError:
    raise ImportError(
        "llama_index is not installed. Please install it with "
        "`pip install llama-index` to use GuardrailsEngine."
    )


class GuardrailsChatEngine(BaseChatEngine):
    _engine_response: AGENT_CHAT_RESPONSE_TYPE

    def __init__(
        self,
        engine: BaseChatEngine,
        guard: Guard,
        guard_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self._engine = engine
        self._guard = guard
        self._guard_kwargs = guard_kwargs or {}
        super().__init__()

    @property
    def guard(self) -> Guard:
        pass

    def engine_api(self, *, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

    def chat(
        self, message: str, chat_history: Optional[List["ChatMessage"]] = None
    ) -> AGENT_CHAT_RESPONSE_TYPE:
        pass

    def _create_chat_response(self, validated_output) -> AGENT_CHAT_RESPONSE_TYPE:
        pass

    async def achat(
        self, message: str, chat_history: Optional[List["ChatMessage"]] = None
    ):
        """Async version of chat."""
        raise NotImplementedError(
            "Async chat is not yet supported in the GuardrailsChatEngine."
        )

    def stream_chat(
        self, message: str, chat_history: Optional[List["ChatMessage"]] = None
    ):
        """Stream chat responses."""
        raise NotImplementedError(
            "Stream chat is not yet supported in the GuardrailsChatEngine."
        )

    async def astream_chat(
        self, message: str, chat_history: Optional[List["ChatMessage"]] = None
    ):
        """Async stream chat responses."""
        raise NotImplementedError(
            "Async stream chat is not yet supported in the GuardrailsChatEngine."
        )

    def reset(self):
        """Reset the chat history."""
        pass

    @property
    def chat_history(self) -> List["ChatMessage"]:
        """Get the chat history."""
        pass

    def _get_prompt_modules(self) -> "PromptMixinType":
        """Get prompt modules."""
        pass
