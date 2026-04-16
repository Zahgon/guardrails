import re
from guardrails.classes.templating.constants_container import ConstantsContainer
from guardrails.classes.templating.namespace_template import NamespaceTemplate

# TODO: Move this to guardrails/constants/__init__.py
# Singleton instance created on import/init
constants = ConstantsContainer()


# TODO: Consolidate this and guardrails/utils/prompt_utils.py
#       into guardrails/utils/templating_utils.py
def substitute_constants(text):
    """Substitute constants in the prompt."""
    pass
