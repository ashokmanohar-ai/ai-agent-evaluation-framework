from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from agent_eval.models.enums import TraceStepType
from agent_eval.models.trace import AgentTrace, ToolCall, TraceStep


def normalize_event_stream(
    events: list[dict[str, Any]],
    run_id: str,
    input_data: dict[str, Any],
    agent_name: str,
    agent_version: str,
) -> AgentTrace:
    """Normalize a conservative subset of orchestration events without inventing evidence."""
    started = datetime.now(UTC)
    steps: list[TraceStep] = []
    calls: list[ToolCall] = []
    final_output: str | dict[str, Any] = ""
    call_arguments: dict[str, dict[str, Any]] = {}

    for index, event in enumerate(events, start=1):
        event_name = str(event.get("event", "unknown"))
        name = str(event.get("name", event_name))
        data = event.get("data", {})
        data = data if isinstance(data, dict) else {"value": data}
        step_type = TraceStepType.MODEL
        if "tool_start" in event_name:
            step_type = TraceStepType.TOOL_CALL
            arguments = data.get("input", {})
            call_arguments[name] = (
                arguments if isinstance(arguments, dict) else {"value": arguments}
            )
        elif "tool_end" in event_name:
            step_type = TraceStepType.TOOL_RESULT
            result = data.get("output")
            calls.append(
                ToolCall(
                    call_id=f"call-{len(calls) + 1}",
                    tool_name=name,
                    arguments=call_arguments.get(name, {}),
                    result=result if isinstance(result, (dict, str)) else str(result),
                    success=True,
                    duration_ms=0,
                )
            )
        elif "chain_end" in event_name:
            step_type = TraceStepType.FINAL
            output = data.get("output", "")
            final_output = output if isinstance(output, (dict, str)) else str(output)
        steps.append(
            TraceStep(
                step_id=f"step-{index}",
                step_type=step_type,
                name=name,
                input=data if step_type == TraceStepType.TOOL_CALL else None,
                output=data if step_type != TraceStepType.TOOL_CALL else None,
                duration_ms=0,
            )
        )

    completed = datetime.now(UTC)
    return AgentTrace(
        run_id=run_id,
        input=input_data,
        steps=steps,
        tool_calls=calls,
        final_output=final_output,
        total_duration_ms=max(0, int((completed - started).total_seconds() * 1000)),
        status="COMPLETED" if final_output else "INCOMPLETE",
        agent_name=agent_name,
        agent_version=agent_version,
        started_at=started,
        completed_at=completed,
    )
