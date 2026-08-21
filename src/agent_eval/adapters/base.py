from __future__ import annotations

from typing import Protocol, runtime_checkable

from agent_eval.models.trace import AgentInput, AgentTrace, ExecutionContext


@runtime_checkable
class AgentAdapter(Protocol):
    """Provider- and orchestration-independent contract for an agent under test."""

    name: str
    version: str

    async def run(self, input_data: AgentInput, context: ExecutionContext) -> AgentTrace:
        """Run an agent and return only evidence observed during execution."""
        ...
