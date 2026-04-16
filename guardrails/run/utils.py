import copy
from string import Template
from typing import Dict, cast, Optional, Tuple

from guardrails.classes.output_type import OutputTypes
from guardrails.llm_providers import (
    LiteLLMCallable,
    AsyncLiteLLMCallable,
    PromptCallableBase,
)
from guardrails.prompt.prompt import Prompt
from guardrails.types.inputs import MessageHistory
from guardrails.prompt.instructions import Instructions


def messages_source(messages: MessageHistory) -> MessageHistory:
    messages_copy = []
    for msg in messages:
        msg_copy = copy.deepcopy(msg)
        content = (
            msg["content"].source
            if isinstance(msg["content"], Prompt)
            or isinstance(msg["content"], Instructions)
            else msg["content"]
        )
        msg_copy["content"] = content
        messages_copy.append(cast(Dict[str, str], msg_copy))
    return messages_copy


def preprocess_prompt_for_string_output(
    prompt_callable: PromptCallableBase,
    instructions: Optional[Instructions],
    prompt: Prompt,
) -> Tuple[Optional[Instructions], Prompt]:
    pass


def preprocess_prompt_for_json_output(
    prompt_callable: PromptCallableBase,
    instructions: Optional[Instructions],
    prompt: Prompt,
    use_xml: bool,
) -> Tuple[Optional[Instructions], Prompt]:
    pass


def preprocess_prompt(
    prompt_callable: PromptCallableBase,
    instructions: Optional[Instructions],
    prompt: Prompt,
    output_type: OutputTypes,
    use_xml: bool,
) -> Tuple[Optional[Instructions], Prompt]:
    pass
