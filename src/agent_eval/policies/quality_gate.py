from __future__ import annotations

from typing import Any

from agent_eval.models.enums import GateStatus, Severity
from agent_eval.models.result import EvaluationRun, GateCheck, GateDecision


def apply_quality_gate(run: EvaluationRun, config: dict[str, Any]) -> GateDecision:
    checks: list[GateCheck] = []
    metric_config = config.get("metrics", {})
    if not isinstance(metric_config, dict):
        raise ValueError("quality gate metrics must be a mapping")
    for metric_name, threshold in metric_config.items():
        if not isinstance(threshold, dict) or "minimum" not in threshold:
            raise ValueError(f"metric gate must define minimum: {metric_name}")
        required = float(threshold["minimum"])
        actual = run.metrics.get(str(metric_name), 0.0)
        status = GateStatus.PASS if actual >= required else GateStatus.FAIL
        checks.append(
            GateCheck(
                metric=str(metric_name),
                actual=actual,
                required=required,
                status=status,
                reason=f"{actual:.3f} {'>=' if status == GateStatus.PASS else '<'} {required:.3f}",
            )
        )

    latency_config = config.get("latency", {})
    if isinstance(latency_config, dict) and "p95_ms" in latency_config:
        maximum = float(latency_config["p95_ms"])
        actual_latency = run.percentiles_ms.get("p95", 0.0)
        status = GateStatus.PASS if actual_latency <= maximum else GateStatus.FAIL
        checks.append(
            GateCheck(
                metric="latency_p95_ms",
                actual=actual_latency,
                required=maximum,
                status=status,
                reason=(
                    f"{actual_latency:.1f}ms "
                    f"{'<=' if status == GateStatus.PASS else '>'} {maximum:.1f}ms"
                ),
            )
        )

    hard_failures = [
        failure
        for case in run.case_results
        for failure in case.failures
        if failure.severity == Severity.CRITICAL
    ]
    weights = config.get("weights", {})
    weighted_score: float | None = None
    if isinstance(weights, dict) and weights:
        total_weight = sum(float(weight) for weight in weights.values())
        if total_weight <= 0:
            raise ValueError("quality gate weights must sum to more than zero")
        weighted_score = (
            sum(
                run.metrics.get(str(metric), 0.0) * float(weight)
                for metric, weight in weights.items()
            )
            / total_weight
        )
    gate_status = (
        GateStatus.FAIL
        if hard_failures or any(check.status == GateStatus.FAIL for check in checks)
        else GateStatus.PASS
    )
    return GateDecision(
        status=gate_status,
        checks=checks,
        hard_failures=hard_failures,
        weighted_score=weighted_score,
    )
