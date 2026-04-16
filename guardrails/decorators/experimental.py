import functools
from guardrails.logger import logger


def experimental(func):
    """Decorator to mark a function as experimental."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pass

    return wrapper
