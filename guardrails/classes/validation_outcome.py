from typing import Iterator, List, Optional, Tuple, Union, Generic, cast

from pydantic import Field
from rich.pretty import pretty_repr

from guardrails_ai.types.validation_outcome import (
    ValidationOutcome as IValidationOutcome,
    OT,
)
from guardrails.actions.reask import ReAsk
from guardrails.classes.history import Call, Iteration
from guardrails.classes.validation.validation_summary import ValidationSummary
from guardrails.constants import pass_status
from guardrails.utils.safe_get import safe_get


class ValidationOutcome(IValidationOutcome, Generic[OT]):
    validation_summaries: Optional[List["ValidationSummary"]] = Field(
        description="The summaries of the validation results.",
        default=[],
        alias="validationSummaries",
    )
    """The summaries of the validation results."""

    model_config = {
        "validate_by_alias": True,
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    @classmethod
    def from_guard_history(cls, call: Call):
        """Create a ValidationOutcome from a history Call object."""
        pass

    def __iter__(
        self,
    ) -> Iterator[
        Union[Optional[str], Optional[OT], Optional[ReAsk], bool, Optional[str]]
    ]:
        """Iterate over the ValidationOutcome's fields."""
        as_tuple: Tuple[
            Optional[str], Optional[OT], Optional[ReAsk], bool, Optional[str]
        ] = (
            self.raw_llm_output,
            self.validated_output,
            self.reask,
            self.validation_passed or False,
            self.error,
        )
        return iter(as_tuple)

    def __getitem__(self, keys):
        """Get a subset of the ValidationOutcome's fields."""
        return iter(getattr(self, k) for k in keys)

    def __str__(self) -> str:
        return pretty_repr(self)

    def to_dict(self):
        return self.model_dump(exclude_none=True, by_alias=True)
