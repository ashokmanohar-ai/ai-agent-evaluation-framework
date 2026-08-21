from importlib.util import find_spec


def openinference_available() -> bool:
    """Return whether optional OpenInference instrumentation is installed."""
    return find_spec("openinference.instrumentation") is not None
