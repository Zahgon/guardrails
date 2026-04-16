import asyncio
import warnings
from itertools import tee
from typing import Any, Dict, Iterator, Optional, AsyncIterator, Iterable, Tuple
from typing_extensions import deprecated

from pydantic import Field, field_serializer, field_validator

from guardrails.classes.generic.arbitrary_model import ArbitraryModel
from guardrails.classes.generic.async_iterable import SerializeableAsyncIterable


warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message="coroutine 'serialize_aiter' was never awaited",
)


# TODO: Move this somewhere that makes sense
def async_to_sync(awaitable):
    pass


async def serialize_aiter(
    async_iter: AsyncIterator,
) -> Tuple[Optional[list[str]], AsyncIterator]:
    pass


# TODO: We might be able to delete this
class LLMResponse(ArbitraryModel):
    """Standard information collection from LLM responses to feed the
    validation loop."""

    # Pydantic Config
    model_config = {
        "validate_by_alias": True,
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    prompt_token_count: Optional[int] = Field(
        default=None,
        alias="promptTokenCount",
        description="The number of tokens in the prompt.",
    )
    response_token_count: Optional[int] = Field(
        default=None,
        alias="responseTokenCount",
        description="The number of tokens in the response.",
    )
    output: str = Field(default="", description="The output from the LLM.")
    stream_output: Optional[Iterator] = Field(
        default=None,
        alias="streamOutput",
        description="A stream of output from the LLM.",
    )
    async_stream_output: Optional[AsyncIterator] = Field(
        default=None,
        alias="asyncStreamOutput",
        description="An async stream of output from the LLM.",
    )

    @field_serializer("stream_output")
    def serialize_stream_output(
        self, stream_output: Iterator | None
    ) -> list[str] | None:
        pass

    @field_validator("stream_output", mode="before")
    @classmethod
    def deserialize_stream_output(cls, stream_output: Any | None) -> Iterator | None:
        pass

    @field_serializer("async_stream_output")
    def serialize_async_stream_output(
        self, async_stream_output: AsyncIterator | None
    ) -> list[str] | None:
        # Legacy serialization logic from previous to_interface implementation
        # We probably need a wrapper class for these.
        pass

    @field_validator("async_stream_output", mode="before")
    @classmethod
    def deserialize_async_stream_output(
        cls, async_stream_output: Any | None
    ) -> AsyncIterator | None:
        pass

    @deprecated("Use LLMResponse.model_dump() instead.")
    def to_interface(self) -> dict[str, Any]:
        pass

    @deprecated("Use LLMResponse.model_dump() instead.")
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    @deprecated("Use LLMResponse.model_validate() instead.")
    def from_interface(cls, i_llm_response: Any) -> "LLMResponse":
        pass

    @classmethod
    @deprecated("Use LLMResponse.model_validate() instead.")
    def from_dict(cls, obj: Any) -> "LLMResponse":
        return cls.model_validate(obj)
