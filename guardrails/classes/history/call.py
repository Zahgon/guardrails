from __future__ import annotations
from typing import Any, Dict, List, Optional, Union, Iterable
from builtins import id as object_id
from pydantic import Field, field_serializer, field_validator, computed_field
from rich.panel import Panel
from rich.pretty import pretty_repr
from rich.tree import Tree
from typing_extensions import deprecated

from guardrails_ai.types import Outcome, ValidationResult

from guardrails.actions.filter import Filter
from guardrails.actions.refrain import Refrain
from guardrails.actions.reask import merge_reask_output
from guardrails.classes.generic.stack import Stack
from guardrails.classes.history.call_inputs import CallInputs
from guardrails.classes.history.iteration import Iteration
from guardrails.classes.generic.arbitrary_model import ArbitraryModel
from guardrails.constants import error_status, fail_status, not_run_status, pass_status
from guardrails.prompt.messages import Messages
from guardrails.prompt import Prompt, Instructions
from guardrails.classes.validation.validator_logs import ValidatorLogs
from guardrails.actions.reask import (
    ReAsk,
    gather_reasks,
    sub_reasks_with_fixed_values,
)
from guardrails.schema.parser import get_value_from_path


# We can't inherit from Iteration because python
# won't let you override a class attribute with a managed attribute
class Call(ArbitraryModel):
    """A Call represents a single execution of a Guard. One Call is created
    each time the user invokes the `Guard.__call__`, `Guard.parse`, or
    `Guard.validate` method.

    Attributes:
        iterations (Stack[Iteration]): A stack of iterations
            for the initial validation round
            and one for each reask that occurs during a Call.
        inputs (CallInputs): The inputs as passed in to
            `Guard.__call__`, `Guard.parse`, or `Guard.validate`
        exception (Optional[Exception]): The exception that interrupted
            the Guard execution.
    """

    _id: str | None = None
    iterations: Stack[Iteration] = Field(
        description="A stack of iterations for each"
        "step/reask that occurred during this call.",
        default_factory=Stack,
    )
    inputs: CallInputs = Field(
        description="The inputs as passed in to Guard.__call__ or Guard.parse",
        default_factory=CallInputs,
    )
    exception: Optional[Exception] = Field(
        description="The exception that interrupted the run.",
        default=None,
    )

    @computed_field
    @property
    def id(self) -> str:
        """The unique identifier for this Call.

        Can be used as an identifier for a specific execution of a
        Guard.
        """
        pass

    @field_serializer("iterations")
    def serialize_iterations(
        self, iterations: Stack[Iteration] | None
    ) -> list[dict[str, Any]] | None:
        pass

    @field_validator("iterations", mode="before")
    @classmethod
    def deserialize_iterations(cls, iterations: Any) -> Stack[Iteration] | None:
        pass

    @field_serializer("exception")
    def serialize_exception(self, exception: Exception | None) -> str | None:
        pass

    @field_validator("exception", mode="before")
    @classmethod
    def deserialize_exception(cls, exception: Any) -> Exception | None:
        pass

    @property
    def prompt_params(self) -> Optional[Dict]:
        """The prompt parameters as provided by the user when initializing or
        calling the Guard."""
        pass

    @property
    def messages(self) -> Optional[Union[Messages, list[dict[str, str]]]]:
        """The messages as provided by the user when initializing or calling
        the Guard."""
        pass

    @property
    def compiled_messages(self) -> Optional[list[dict[str, str]]]:
        """The initial compiled messages that were passed to the LLM on the
        first call."""
        pass

    @property
    def reask_messages(self) -> Stack[Messages]:
        """The compiled messages used during reasks.

        Does not include the initial messages.
        """
        pass

    @property
    def logs(self) -> Stack[str]:
        """Returns all logs from all iterations as a stack."""
        pass

    @property
    def tokens_consumed(self) -> Optional[int]:
        """Returns the total number of tokens consumed during all iterations
        with this call."""
        pass

    @property
    def prompt_tokens_consumed(self) -> Optional[int]:
        """Returns the total number of prompt tokens consumed during all
        iterations with this call."""
        pass

    @property
    def completion_tokens_consumed(self) -> Optional[int]:
        """Returns the total number of completion tokens consumed during all
        iterations with this call."""
        pass

    @property
    def raw_outputs(self) -> Stack[str]:
        """The exact outputs from all LLM calls."""
        pass

    @property
    def parsed_outputs(self) -> Stack[Union[str, List, Dict]]:
        """The outputs from the LLM after undergoing parsing but before
        validation."""
        pass

    @property
    def validation_response(self) -> Optional[Union[str, List, Dict, ReAsk]]:
        """The aggregated responses from the validation process across all
        iterations within the current call.

        This value could contain ReAsks.
        """
        pass

    @property
    def fixed_output(self) -> Optional[Union[str, List, Dict]]:
        """The cumulative output from the validation process across all current
        iterations with any automatic fixes applied.

        Could still contain ReAsks if a fix was not available.
        """
        pass

    @property
    def guarded_output(self) -> Optional[Union[str, List, Dict]]:
        """The complete validated output after all stages of validation are
        completed.

        This property contains the aggregate validated output after all
        validation stages have been completed. Some values in the
        validated output may be "fixed" values that were corrected
        during validation.

        This will only have a value if the Guard is in a passing state
        OR if the action is no-op.
        """
        pass

    @property
    def reasks(self) -> Stack[ReAsk]:
        """Reasks generated during validation that could not be automatically
        fixed.

        These would be incorporated into the prompt for the next LLM
        call if additional reasks were granted.
        """
        pass

    @property
    def validator_logs(self) -> Stack[ValidatorLogs]:
        """The results of each individual validation performed on the LLM
        responses during all iterations."""
        pass

    @property
    def error(self) -> Optional[str]:
        """The error message from any exception that raised and interrupted the
        run."""
        if self.exception:
            return str(self.exception)
        elif self.iterations.empty():
            return None
        return self.iterations.last.error  # type: ignore

    @property
    def failed_validations(self) -> Stack[ValidatorLogs]:
        """The validator logs for any validations that failed during the
        entirety of the run."""
        pass

    def _has_unresolved_failures(self) -> bool:
        # Check for unresolved ReAsks
        if len(self.reasks) > 0:
            return True

        # Check for scenario where no specified on-fail's produced an unfixed ReAsk,
        #   but valdiation still failed (i.e. Refrain or NoOp).
        output = self.fixed_output
        for failure in self.failed_validations:
            value = get_value_from_path(output, failure.property_path)
            if (
                # NOTE: this means on_fail="fix" was applied
                #       to a Validator without a programmatic fix.
                (value is None and failure.value_before_validation is not None)
                or value == failure.value_before_validation
                or isinstance(failure.value_after_validation, Refrain)
                or isinstance(failure.value_after_validation, Filter)
            ):
                return True

        # No ReAsks and no unresolved failed validations
        return False

    @property
    def status(self) -> str:
        """Returns the cumulative status of the run based on the validity of
        the final merged output."""
        if self.iterations.empty():
            return not_run_status
        elif self.error:
            return error_status
        elif self._has_unresolved_failures():
            return fail_status
        return pass_status

    @property
    def tree(self) -> Tree:
        """Returns the tree."""
        pass

    def __str__(self) -> str:
        return pretty_repr(self)

    @deprecated("Use Call.model_dump() instead.")
    def to_interface(self) -> dict[str, Any]:
        pass

    @deprecated("Use Call.model_dump() instead.")
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    @deprecated("Use Call.model_validate() instead.")
    def from_interface(cls, i_call: Any) -> "Call":
        pass

    # TODO: Necessary to GET /guards/{guard_name}/history/{call_id}
    @classmethod
    @deprecated("Use Call.model_validate() instead.")
    def from_dict(cls, obj: Any) -> "Call":
        return cls.model_validate(obj)
