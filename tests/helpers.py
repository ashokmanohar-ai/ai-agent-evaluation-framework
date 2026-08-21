from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from agent_eval.models.dataset import EvaluationCase, EvaluationExpectations
from agent_eval.models.enums import TraceStepType
from agent_eval.models.trace import AgentTrace, ApprovalEvent, ToolCall, TraceStep


def make_case(**expectation_overrides: Any) -> EvaluationCase:
    values: dict[str, Any] = {"task": "test", **expectation_overrides}
    return EvaluationCase(
        id="TEST-001",
        description="deterministic evaluator test",
        input={"message": "test", "scenario": "test"},
        expectations=EvaluationExpectations(**values),
        tags=["test"],
    )


def make_trace(
    *,
    calls: list[ToolCall] | None = None,
    final_output: str | dict[str, Any] = "done",
    step_names: list[str] | None = None,
    approvals: list[ApprovalEvent] | None = None,
    duration_ms: int = 10,
) -> AgentTrace:
    started = datetime.now(UTC)
    steps = [
        TraceStep(
            step_id=f"step-{index}",
            step_type=TraceStepType.ROUTING,
            name=name,
            timestamp=started + timedelta(milliseconds=index),
        )
        for index, name in enumerate(step_names or [], start=1)
    ]
    return AgentTrace(
        run_id="run-test",
        input={"message": "test"},
        steps=steps,
        tool_calls=calls or [],
        approvals=approvals or [],
        final_output=final_output,
        total_duration_ms=duration_ms,
        status="COMPLETED",
        agent_name="test",
        agent_version="1.0.0",
        started_at=started,
        completed_at=started + timedelta(milliseconds=duration_ms),
    )


def tool_call(
    name: str,
    arguments: dict[str, Any],
    result: str | dict[str, Any] | None,
    *,
    success: bool = True,
    attempt: int = 1,
    timestamp: datetime | None = None,
) -> ToolCall:
    return ToolCall(
        call_id=f"call-{name}-{attempt}",
        tool_name=name,
        arguments=arguments,
        result=result,
        success=success,
        duration_ms=1,
        attempt=attempt,
        timestamp=timestamp or datetime.now(UTC),
    )
