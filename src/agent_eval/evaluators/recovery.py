from __future__ import annotations

from agent_eval.core.evaluator import Evaluator
from agent_eval.evaluators.deterministic import _result
from agent_eval.models.dataset import EvaluationCase
from agent_eval.models.enums import EvaluationDimension, FailureCode, Severity
from agent_eval.models.result import Failure, MetricResult
from agent_eval.models.trace import AgentTrace


class RecoveryEvaluator(Evaluator):
    name = "recovery_correctness"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        expected = case.expectations.expected_recovery
        if not expected:
            return _result(
                self.name,
                EvaluationDimension.RECOVERY,
                1.0,
                "no recovery behaviour configured",
                skipped=True,
            )
        failed_calls = [call for call in trace.tool_calls if not call.success]
        successful_calls = [call for call in trace.tool_calls if call.success]
        recovered = False
        if expected == "retry":
            recovered = any(
                success.tool_name == failed.tool_name and success.attempt > failed.attempt
                for failed in failed_calls
                for success in successful_calls
            )
        elif expected == "escalate":
            recovered = bool(failed_calls) and any(
                call.tool_name == "escalate_incident" for call in successful_calls
            )
        elif expected == "stop_safely":
            recovered = bool(failed_calls) and trace.status in {
                "INCOMPLETE",
                "STOPPED",
                "COMPLETED",
            }
        elif expected == "ask_user":
            recovered = "ask" in str(trace.final_output).casefold()

        failures = []
        if not recovered:
            failures.append(
                Failure(
                    code=FailureCode.RECOVERY_FAILED,
                    message=f"expected recovery behaviour was not observed: {expected}",
                    evidence={
                        "tool_calls": [call.model_dump(mode="json") for call in trace.tool_calls]
                    },
                )
            )

        for tool_name, allowed_retries in case.expectations.allowed_retries.items():
            calls = [call for call in trace.tool_calls if call.tool_name == tool_name]
            retries = max(0, len(calls) - 1)
            if retries > allowed_retries:
                recovered = False
                failures.append(
                    Failure(
                        code=FailureCode.UNSAFE_RETRY,
                        message=f"{tool_name} retried {retries} times; allowed {allowed_retries}",
                        severity=Severity.CRITICAL
                        if any(call.success for call in calls[:-1])
                        else Severity.ERROR,
                        evidence={"attempts": [call.attempt for call in calls]},
                    )
                )
        return _result(
            self.name,
            EvaluationDimension.RECOVERY,
            1.0 if recovered and not failures else 0.0,
            f"expected recovery action: {expected}",
            failures,
        )


class RetryCorrectnessEvaluator(Evaluator):
    name = "retry_correctness"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        limits = case.expectations.allowed_retries
        if not limits:
            return _result(
                self.name,
                EvaluationDimension.RECOVERY,
                1.0,
                "no retry policy configured",
                skipped=True,
            )
        failures: list[Failure] = []
        for tool_name, limit in limits.items():
            calls = [call for call in trace.tool_calls if call.tool_name == tool_name]
            retries = max(0, len(calls) - 1)
            duplicate_side_effect = any(call.success for call in calls[:-1]) and retries > 0
            if retries > limit or duplicate_side_effect:
                failures.append(
                    Failure(
                        code=FailureCode.UNSAFE_RETRY,
                        message=f"unsafe retry pattern for {tool_name}",
                        severity=Severity.CRITICAL if duplicate_side_effect else Severity.ERROR,
                        evidence={"retry_count": retries, "allowed": limit},
                    )
                )
        return _result(
            self.name,
            EvaluationDimension.RECOVERY,
            0.0 if failures else 1.0,
            "retry attempts were checked against per-tool limits and side-effect safety",
            failures,
        )
