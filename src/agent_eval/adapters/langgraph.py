from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol

from agent_eval.models.trace import AgentInput, AgentTrace, ExecutionContext
from agent_eval.tracing.normalizer import normalize_event_stream


class LangGraphLike(Protocol):
    def astream_events(
        self, input: dict[str, Any], *, version: str
    ) -> AsyncIterator[dict[str, Any]]: ...


class LangGraphAdapter:
    """Optional adapter that converts LangGraph v2 events to the framework trace format."""

    def __init__(self, graph: LangGraphLike, name: str, version: str) -> None:
        self.graph = graph
        self.name = name
        self.version = version

    async def run(self, input_data: AgentInput, context: ExecutionContext) -> AgentTrace:
        events: list[dict[str, Any]] = []
        async for event in self.graph.astream_events(input_data.model_dump(), version="v2"):
            events.append(dict(event))
        return normalize_event_stream(
            events=events,
            run_id=context.run_id,
            input_data=input_data.model_dump(),
            agent_name=self.name,
            agent_version=self.version,
        )
