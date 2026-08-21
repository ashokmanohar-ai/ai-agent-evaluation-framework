from __future__ import annotations

from collections.abc import Awaitable, Callable

from agent_eval.models.trace import AgentInput, AgentTrace, ExecutionContext


class GenericAgentAdapter:
    """Adapts any async callable returning a normalized trace."""

    def __init__(
        self,
        name: str,
        version: str,
        runner: Callable[[AgentInput, ExecutionContext], Awaitable[AgentTrace]],
    ) -> None:
        self.name = name
        self.version = version
        self._runner = runner

    async def run(self, input_data: AgentInput, context: ExecutionContext) -> AgentTrace:
        trace = await self._runner(input_data, context)
        if trace.agent_name != self.name or trace.agent_version != self.version:
            raise ValueError("adapter identity does not match returned trace")
        return trace
