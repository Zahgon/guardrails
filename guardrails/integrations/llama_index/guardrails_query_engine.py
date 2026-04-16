from typing import Any, Optional, Dict, List, cast
from guardrails import Guard
from guardrails.errors import ValidationError
from guardrails.classes.validation_outcome import ValidationOutcome


try:
    import llama_index  # noqa: F401
    from llama_index.core.query_engine import BaseQueryEngine
    from llama_index.core.schema import QueryBundle
    from llama_index.core.callbacks import CallbackManager
    from llama_index.core.base.response.schema import (
        RESPONSE_TYPE,
        Response,
        StreamingResponse,
        AsyncStreamingResponse,
        PydanticResponse,
    )
    from llama_index.core.prompts.mixin import PromptMixinType
except ImportError:
    raise ImportError(
        "llama_index is not installed. Please install it with "
        "`pip install llama-index` to use GuardrailsEngine."
    )


class GuardrailsQueryEngine(BaseQueryEngine):
    _engine_response: RESPONSE_TYPE

    def __init__(
        self,
        engine: BaseQueryEngine,
        guard: Guard,
        guard_kwargs: Optional[Dict[str, Any]] = None,
        callback_manager: Optional["CallbackManager"] = None,
    ):
        self._engine = engine
        self._guard = guard
        self._guard_kwargs = guard_kwargs or {}
        super().__init__(callback_manager)

    @property
    def guard(self) -> Guard:
        pass

    def engine_api(self, *, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

    def _query(self, query_bundle: "QueryBundle") -> RESPONSE_TYPE:
        pass

    def _update_response_metadata(self, validated_output):
        pass

    async def _aquery(self, query_bundle: "QueryBundle") -> "RESPONSE_TYPE":
        """Async version of _query."""
        pass

    def _get_prompt_modules(self) -> "PromptMixinType":
        """Get prompt modules."""
        pass
