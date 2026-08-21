from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agent_eval.models.enums import GateStatus
from agent_eval.models.result import EvaluationRun
from agent_eval.regression.baseline import Baseline


class RegressionCheck(BaseModel):
    metric: str
    baseline: float
    current: float
    drop: float
    allowed_drop: float
    status: GateStatus


class RegressionDecision(BaseModel):
    status: GateStatus
    checks: list[RegressionCheck]
    warnings: list[str] = Field(default_factory=list)


def compare_baseline(
    baseline: Baseline,
    current: EvaluationRun,
    config: dict[str, Any],
) -> RegressionDecision:
    warnings: list[str] = []
    if baseline.dataset_version != current.dataset_version:
        warnings.append("dataset versions differ; interpret comparison with caution")
    if baseline.evaluator_version != current.reproducibility.evaluator_version:
        warnings.append("evaluator versions differ; metric comparability is not guaranteed")
    thresholds = config.get("regression", {})
    if not isinstance(thresholds, dict):
        raise ValueError("regression configuration must be a mapping")
    checks: list[RegressionCheck] = []
    for metric, settings in thresholds.items():
        if not isinstance(settings, dict) or "max_drop" not in settings:
            raise ValueError(f"regression metric missing max_drop: {metric}")
        baseline_value = baseline.metrics.get(str(metric), 0.0)
        current_value = current.metrics.get(str(metric), 0.0)
        drop = baseline_value - current_value
        allowed = float(settings["max_drop"])
        checks.append(
            RegressionCheck(
                metric=str(metric),
                baseline=baseline_value,
                current=current_value,
                drop=drop,
                allowed_drop=allowed,
                status=GateStatus.PASS if drop <= allowed else GateStatus.FAIL,
            )
        )
    status = (
        GateStatus.FAIL
        if any(check.status == GateStatus.FAIL for check in checks)
        else GateStatus.PASS
    )
    return RegressionDecision(status=status, checks=checks, warnings=warnings)
