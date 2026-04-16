from copy import deepcopy
from typing import Any, Dict, Optional, Union, cast
import json
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable, RunnableConfig
from guardrails.classes.input_type import InputType
from guardrails.classes.output_type import OT


class BaseRunnable(Runnable):
    name: Union[str, None]

    def invoke(
        self,
        input: InputType,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> InputType:
        pass

    def _process_input(self, input: InputType) -> InputType:
        pass

    def _validate(self, input: str) -> OT:
        raise NotImplementedError
