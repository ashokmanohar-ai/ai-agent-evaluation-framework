from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from agent_eval.models.enums import TraceStepType


class AgentInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    message: str
    user_id: str = "demo-user"


class ExecutionContext(BaseModel):
    run_id: str
    case_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelUsage(BaseModel):
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None
    currency: str | None = None

    @property
    def total_tokens(self) -> int | None:
        if self.input_tokens is None or self.output_tokens is None:
            return None
        return self.input_tokens + self.output_tokens


class ApprovalEvent(BaseModel):
    action: str
    requested_at: datetime
    decision: str
    decided_at: datetime | None = None
    actor: str = "human"


class ToolCall(BaseModel):
    call_id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | str | None = None
    success: bool
    duration_ms: int = Field(ge=0)
    attempt: int = Field(default=1, ge=1)
    error: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TraceStep(BaseModel):
    step_id: str
    step_type: TraceStepType
    name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input: dict[str, Any] | None = None
    output: dict[str, Any] | str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    agent_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentTrace(BaseModel):
    run_id: str
    input: dict[str, Any]
    steps: list[TraceStep]
    tool_calls: list[ToolCall] = Field(default_factory=list)
    approvals: list[ApprovalEvent] = Field(default_factory=list)
    final_output: str | dict[str, Any]
    total_duration_ms: int = Field(ge=0)
    model_usage: list[ModelUsage] = Field(default_factory=list)
    status: str
    errors: list[str] = Field(default_factory=list)
    agent_name: str
    agent_version: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def tool_names(self, successful_only: bool = False) -> list[str]:
        calls = self.tool_calls
        if successful_only:
            calls = [call for call in calls if call.success]
        return [call.tool_name for call in calls]

    def step_names(self) -> list[str]:
        return [step.name for step in self.steps]

    def total_tokens(self) -> int | None:
        values = [usage.total_tokens for usage in self.model_usage]
        known = [value for value in values if value is not None]
        return sum(known) if known else None
