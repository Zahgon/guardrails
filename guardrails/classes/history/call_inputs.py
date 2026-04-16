from __future__ import annotations
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional
from typing_extensions import deprecated

from pydantic import Field, field_serializer, field_validator

from guardrails.classes.history.inputs import Inputs
from guardrails.classes.generic.arbitrary_model import ArbitraryModel
from guardrails.prompt.base_prompt import BasePrompt


class CallInputs(Inputs, ArbitraryModel):
    """CallInputs represent the input data that is passed into the Guard from
    the user.

    Inherits from Inputs with the below overrides and additional
    attributes.
    """

    llm_api: Optional[Callable[[Any], Awaitable[Any]]] = Field(
        description="The LLM function provided by the user"
        "during Guard.__call__ or Guard.parse.",
        default=None,
        alias="llmApi",
    )
    llm_output: Optional[str] = Field(
        default=None,
        description="The string output from an external LLM call provided by the user"
        " via Guard.parse.",
        alias="llmOutput",
    )
    messages: Optional[list[dict[str, str]]] = Field(
        description="The messages as provided by the user.", default=None
    )
    prompt_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parameters to be formatted into the messages.",
        alias="promptParams",
    )
    num_reasks: Optional[int] = Field(
        default=None,
        description="The total number of times the LLM can be called to correct output"
        " excluding the initial call.",
        alias="numReasks",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional data to be used by Validators during execution time.",
    )
    full_schema_reask: Optional[bool] = Field(
        default=None,
        description="Whether to perform reasks for the entire schema rather than for"
        " individual fields.",
        alias="fullSchemaReask",
    )
    stream: Optional[bool] = Field(
        default=None, description="Whether to use streaming."
    )
    args: List[Any] = Field(
        description="Additional arguments for the LLM as provided by the user.",
        default_factory=list,
    )
    kwargs: Dict[str, Any] = Field(
        description="Additional keyword-arguments for the LLM as provided by the user.",
        default_factory=dict,
    )

    @field_serializer("llm_api")
    def serialize_llm_api(
        self, llm_api: Callable[[Any], Awaitable[Any]] | None
    ) -> str | None:
        pass

    @field_validator("llm_api", mode="before")
    @classmethod
    def deserialize_llm_api(
        cls, llm_api: Any
    ) -> Callable[[Any], Awaitable[Any]] | None:
        pass

    @field_validator("messages", mode="before")
    @classmethod
    def deserialize_messages(cls, messages: Any) -> list[dict[str, str]] | None:
        pass

    @field_serializer("kwargs")
    def serialize_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        pass

    @deprecated("Use CallInputs.model_dump() instead.")
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    @deprecated("Use CallInputs.model_validate() instead.")
    def from_interface(cls, i_call_inputs: Any) -> "CallInputs":
        pass

    @classmethod
    @deprecated("Use CallInputs.model_validate() instead.")
    def from_dict(cls, obj: Any):
        return cls.model_validate(obj)
