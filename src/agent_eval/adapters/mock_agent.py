from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from agent_eval.models.enums import TraceStepType
from agent_eval.models.trace import (
    AgentInput,
    AgentTrace,
    ApprovalEvent,
    ExecutionContext,
    ModelUsage,
    ToolCall,
    TraceStep,
)


class _TraceBuilder:
    def __init__(self, run_id: str, input_data: AgentInput) -> None:
        self.run_id = run_id
        self.input_data = input_data
        self.started_at = datetime.now(UTC)
        self.clock = self.started_at
        self.steps: list[TraceStep] = []
        self.calls: list[ToolCall] = []
        self.approvals: list[ApprovalEvent] = []

    def _tick(self, milliseconds: int = 5) -> datetime:
        self.clock += timedelta(milliseconds=milliseconds)
        return self.clock

    def step(
        self,
        step_type: TraceStepType,
        name: str,
        *,
        input: dict[str, Any] | None = None,
        output: dict[str, Any] | str | None = None,
        agent_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        timestamp = self._tick()
        self.steps.append(
            TraceStep(
                step_id=f"step-{len(self.steps) + 1}",
                step_type=step_type,
                name=name,
                timestamp=timestamp,
                input=input,
                output=output,
                duration_ms=5,
                agent_name=agent_name,
                metadata=metadata or {},
            )
        )

    def route(self, source: str, destination: str, payload: dict[str, Any]) -> None:
        self.step(
            TraceStepType.ROUTING,
            destination,
            input=payload,
            output={"source": source, "destination": destination},
            agent_name=source,
        )

    def approve(self, action: str, decision: str) -> None:
        requested_at = self._tick()
        decided_at = self._tick()
        event = ApprovalEvent(
            action=action,
            requested_at=requested_at,
            decision=decision,
            decided_at=decided_at,
        )
        self.approvals.append(event)
        self.steps.append(
            TraceStep(
                step_id=f"step-{len(self.steps) + 1}",
                step_type=TraceStepType.HUMAN_APPROVAL,
                name=action,
                timestamp=requested_at,
                input={"action": action},
                output={"decision": decision},
                duration_ms=5,
            )
        )

    def tool(
        self,
        name: str,
        arguments: dict[str, Any],
        result: dict[str, Any] | str | None,
        *,
        success: bool = True,
        attempt: int = 1,
        error: str | None = None,
    ) -> None:
        call_id = f"call-{len(self.calls) + 1}"
        called_at = self._tick()
        self.steps.append(
            TraceStep(
                step_id=f"step-{len(self.steps) + 1}",
                step_type=TraceStepType.TOOL_CALL,
                name=name,
                timestamp=called_at,
                input=arguments,
                duration_ms=5,
                metadata={"call_id": call_id, "attempt": attempt},
            )
        )
        completed_at = self._tick()
        self.calls.append(
            ToolCall(
                call_id=call_id,
                tool_name=name,
                arguments=arguments,
                result=result,
                success=success,
                duration_ms=5,
                attempt=attempt,
                error=error,
                timestamp=called_at,
            )
        )
        self.steps.append(
            TraceStep(
                step_id=f"step-{len(self.steps) + 1}",
                step_type=TraceStepType.TOOL_RESULT,
                name=name,
                timestamp=completed_at,
                output=result if success else {"error": error or "tool failure"},
                duration_ms=5,
                metadata={"call_id": call_id, "success": success, "attempt": attempt},
            )
        )

    def finish(self, output: dict[str, Any] | str, status: str = "COMPLETED") -> AgentTrace:
        self.step(TraceStepType.FINAL, "final", output=output)
        return AgentTrace(
            run_id=self.run_id,
            input=self.input_data.model_dump(),
            steps=self.steps,
            tool_calls=self.calls,
            approvals=self.approvals,
            final_output=output,
            total_duration_ms=max(1, int((self.clock - self.started_at).total_seconds() * 1000)),
            model_usage=[ModelUsage(provider="mock", model="deterministic-rule-engine")],
            status=status,
            agent_name="mock",
            agent_version="1.0.0",
            started_at=self.started_at,
            completed_at=self.clock,
        )


class MockAgentAdapter:
    """Deterministic, side-effect-free agent used for CI and framework demonstrations."""

    name = "mock"
    version = "1.0.0"

    async def run(self, input_data: AgentInput, context: ExecutionContext) -> AgentTrace:
        data = input_data.model_dump()
        scenario = str(data.get("scenario", "knowledge"))
        builder = _TraceBuilder(context.run_id, input_data)
        result: dict[str, Any]
        builder.step(TraceStepType.MODEL, "plan", input={"scenario": scenario})

        if scenario == "ticket_status":
            ticket_id = str(data.get("ticket_id", "INC-001"))
            result = {"ticket_id": ticket_id, "status": "OPEN", "owner": input_data.user_id}
            builder.tool("get_ticket", {"ticket_id": ticket_id}, result)
            return builder.finish(result)

        if scenario == "create_ticket":
            summary = str(data.get("summary", "Demo incident"))
            result = {"ticket_id": "INC-NEW-1001", "status": "CREATED", "summary": summary}
            builder.tool(
                "create_ticket", {"summary": summary, "user_id": input_data.user_id}, result
            )
            return builder.finish(result)

        if scenario in {"service_status", "recovery_status"}:
            service = str(data.get("service", "payments"))
            if scenario == "recovery_status":
                builder.tool(
                    "get_service_status",
                    {"service": service},
                    None,
                    success=False,
                    attempt=1,
                    error="timeout",
                )
                builder.step(TraceStepType.ROUTING, "retry_once", output={"reason": "timeout"})
            result = {"service": service, "status": "OPERATIONAL"}
            builder.tool(
                "get_service_status",
                {"service": service},
                result,
                attempt=2 if scenario == "recovery_status" else 1,
            )
            return builder.finish(result)

        if scenario == "recovery_escalate":
            service = str(data.get("service", "identity"))
            builder.tool(
                "get_service_status",
                {"service": service},
                None,
                success=False,
                error="service unavailable",
            )
            result = {"incident_id": "MAJOR-001", "status": "ESCALATED"}
            builder.tool("escalate_incident", {"service": service, "reason": "unavailable"}, result)
            return builder.finish(result)

        if scenario == "knowledge":
            query = str(data.get("query", input_data.message))
            result = {"answer": "Password resets require verified identity.", "source": "KB-SEC-01"}
            builder.tool("search_knowledge", {"query": query}, result)
            return builder.finish(result)

        if scenario == "policy":
            policy = str(data.get("policy", "refund"))
            result = {"policy": policy, "answer": "Refunds are available within 30 days."}
            builder.tool("lookup_policy", {"policy": policy}, result)
            return builder.finish(result)

        if scenario == "access_request":
            resource = str(data.get("resource", "finance-dashboard"))
            entitlement = {"user_id": input_data.user_id, "resource": resource, "eligible": True}
            builder.tool(
                "check_user_entitlement",
                {"user_id": input_data.user_id, "resource": resource},
                entitlement,
            )
            builder.approve("request_access", "APPROVED")
            result = {"request_id": "REQ-1001", "status": "PENDING_APPROVAL"}
            builder.tool(
                "request_access",
                {"user_id": input_data.user_id, "resource": resource},
                result,
            )
            return builder.finish(result)

        if scenario == "approval_rejected":
            resource = str(data.get("resource", "production-admin"))
            builder.tool(
                "check_user_entitlement",
                {"user_id": input_data.user_id, "resource": resource},
                {"eligible": False},
            )
            builder.approve("request_access", "REJECTED")
            return builder.finish({"status": "NOT_EXECUTED", "reason": "approval rejected"})

        if scenario == "schedule_support":
            slot = str(data.get("slot", "2026-08-22T10:00:00Z"))
            result = {"booking_id": "BOOK-101", "slot": slot, "status": "SCHEDULED"}
            builder.tool("schedule_support", {"slot": slot}, result)
            return builder.finish(result)

        if scenario == "cross_user":
            target_user = str(data.get("target_user", "other-user"))
            result = {"authorized": False, "target_user": target_user}
            builder.tool(
                "check_user_entitlement",
                {"user_id": input_data.user_id, "target_user": target_user},
                result,
            )
            return builder.finish({"status": "DENIED", "reason": "not authorized"})

        if scenario == "multi_agent":
            expected_agent = str(data.get("expected_agent", "PolicyAgent"))
            builder.route("Supervisor", expected_agent, {"message": input_data.message})
            if expected_agent == "PolicyAgent":
                result = {"policy": "refund", "answer": "Refunds are available within 30 days."}
                builder.tool("lookup_policy", {"policy": "refund"}, result)
            else:
                result = {"ticket_id": "INC-001", "status": "OPEN"}
                builder.tool("get_ticket", {"ticket_id": "INC-001"}, result)
            builder.route(expected_agent, "Supervisor", {"result": result})
            return builder.finish(result)

        if scenario == "memory_isolation":
            builder.step(
                TraceStepType.MEMORY,
                "read_memory",
                input={"user_id": input_data.user_id},
                output={"region": str(data.get("own_region", "India"))},
            )
            return builder.finish({"region": str(data.get("own_region", "India"))})

        if scenario in {"prompt_injection", "tool_injection", "forbidden_action"}:
            return builder.finish(
                {"status": "REFUSED", "reason": "request conflicts with access and safety policy"}
            )

        return builder.finish({"answer": "No action was required.", "status": "COMPLETED"})
