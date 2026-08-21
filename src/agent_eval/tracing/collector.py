from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any

from opentelemetry import trace


def evaluation_span(
    name: str, attributes: dict[str, str | int | float | bool]
) -> AbstractContextManager[Any]:
    tracer = trace.get_tracer("agent_eval")
    if not trace.get_current_span().is_recording() and not tracer:
        return nullcontext()
    return tracer.start_as_current_span(name, attributes=attributes)
