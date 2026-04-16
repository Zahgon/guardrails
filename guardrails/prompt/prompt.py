"""The LLM prompt."""

from string import Template

from guardrails.utils.templating_utils import get_template_variables

from .base_prompt import BasePrompt


class Prompt(BasePrompt):
    """Prompt class.

    The prompt is passed to the LLM as primary instructions.
    """

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Prompt) and self.source == __value.source

    def format(self, **kwargs) -> "Prompt":
        """Format the prompt using the given keyword arguments."""
        pass
