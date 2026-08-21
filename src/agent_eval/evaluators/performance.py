from __future__ import annotations

from agent_eval.core.evaluator import Evaluator
from agent_eval.evaluators.deterministic import _result
from agent_eval.models.dataset import EvaluationCase
from agent_eval.models.enums import EvaluationDimension, FailureCode
from agent_eval.models.result import Failure, MetricResult
from agent_eval.models.trace import AgentTrace


class LatencyEvaluator(Evaluator):
    name = "latency"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        maximum = case.expectations.maximum_latency_ms
        if maximum is None:
            return _result(
                self.name,
                EvaluationDimension.PERFORMANCE,
                1.0,
                "no case latency budget configured",
                skipped=True,
            )
        breached = trace.total_duration_ms > maximum
        failures = []
        if breached:
            failures.append(
                Failure(
                    code=FailureCode.LATENCY_BREACH,
                    message=f"latency {trace.total_duration_ms}ms exceeded {maximum}ms",
                    evidence={"actual_ms": trace.total_duration_ms, "maximum_ms": maximum},
                )
            )
        return _result(
            self.name,
            EvaluationDimension.PERFORMANCE,
            0.0 if breached else 1.0,
            f"observed {trace.total_duration_ms}ms against {maximum}ms budget",
            failures,
            {"duration_ms": trace.total_duration_ms, "maximum_ms": maximum},
        )


class TokenUsageEvaluator(Evaluator):
    name = "token_usage"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        maximum = case.expectations.maximum_tokens
        total = trace.total_tokens()
        if maximum is None or total is None:
            return _result(
                self.name,
                EvaluationDimension.PERFORMANCE,
                1.0,
                "token budget or provider-reported usage is unavailable; no value was fabricated",
                details={"provider_reported_tokens": total, "maximum_tokens": maximum},
                skipped=True,
            )
        breached = total > maximum
        failures = []
        if breached:
            failures.append(
                Failure(
                    code=FailureCode.TOKEN_BUDGET_BREACH,
                    message=f"token usage {total} exceeded {maximum}",
                    evidence={"actual": total, "maximum": maximum},
                )
            )
        return _result(
            self.name,
            EvaluationDimension.PERFORMANCE,
            0.0 if breached else 1.0,
            f"provider reported {total} tokens",
            failures,
        )


class CostEvaluator(Evaluator):
    name = "cost"

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        known_costs = [usage.cost for usage in trace.model_usage if usage.cost is not None]
        if not known_costs:
            return _result(
                self.name,
                EvaluationDimension.PERFORMANCE,
                1.0,
                "provider cost was unavailable; no price or cost was fabricated",
                skipped=True,
            )
        return _result(
            self.name,
            EvaluationDimension.PERFORMANCE,
            1.0,
            f"provider-reported cost total: {sum(known_costs):.6f}",
            details={"cost": sum(known_costs)},
        )
