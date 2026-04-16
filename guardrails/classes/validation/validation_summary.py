# TODO Temp to update once generated class is in
from typing import Iterator, List

from guardrails.classes.generic.arbitrary_model import ArbitraryModel
from guardrails_ai.types import FailResult
from guardrails.classes.validation.validator_logs import ValidatorLogs
from guardrails_ai.types import ValidationSummary as IValidationSummary


class ValidationSummary(IValidationSummary, ArbitraryModel):
    @staticmethod
    def _generate_summaries_from_validator_logs(
        validator_logs: List[ValidatorLogs],
    ) -> Iterator["ValidationSummary"]:
        """Generate a list of ValidationSummary objects from a list of
        ValidatorLogs objects.

        Using an iterator to allow serializing the summaries to other
        formats.
        """
        pass

    @staticmethod
    def from_validator_logs(
        validator_logs: List[ValidatorLogs],
    ) -> List["ValidationSummary"]:
        pass

    @staticmethod
    def from_validator_logs_only_fails(
        validator_logs: List[ValidatorLogs],
    ) -> List["ValidationSummary"]:
        pass
