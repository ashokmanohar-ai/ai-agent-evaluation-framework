from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from agent_eval.models.enums import (
    EvaluationDimension,
    FailureCode,
    GateStatus,
    MetricStatus,
    Severity,
)
from agent_eval.models.trace import AgentTrace


class Failure(BaseModel):
    code: FailureCode
    message: str
    severity: Severity = Severity.ERROR
    evidence: dict[str, Any] = Field(default_factory=dict)


class MetricResult(BaseModel):
    name: str
    dimension: EvaluationDimension
    score: float = Field(ge=0.0, le=1.0)
    status: MetricStatus
    rationale: str
    failures: list[Failure] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    evaluator_version: str = "1.0.0"


class CaseResult(BaseModel):
    case_id: str
    description: str
    status: MetricStatus
    trace: AgentTrace
    metrics: dict[str, MetricResult]
    tags: list[str]
    failures: list[Failure] = Field(default_factory=list)
    run_index: int = 1


class GateCheck(BaseModel):
    metric: str
    actual: float
    required: float
    status: GateStatus
    reason: str


class GateDecision(BaseModel):
    status: GateStatus
    checks: list[GateCheck]
    hard_failures: list[Failure] = Field(default_factory=list)
    weighted_score: float | None = None


class ReproducibilityMetadata(BaseModel):
    framework_version: str
    agent_name: str
    agent_version: str
    dataset_version: str
    evaluator_version: str
    judge_provider: str
    judge_model: str
    judge_prompt_version: str
    temperature: float
    runs_per_case: int
    python_version: str


class EvaluationRun(BaseModel):
    run_id: str
    agent_name: str
    agent_version: str
    dataset_version: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    case_results: list[CaseResult] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    percentiles_ms: dict[str, float] = Field(default_factory=dict)
    tag_metrics: dict[str, dict[str, float]] = Field(default_factory=dict)
    failure_summary: dict[str, int] = Field(default_factory=dict)
    stability: float | None = None
    gate: GateDecision | None = None
    reproducibility: ReproducibilityMetadata

    @property
    def passed_cases(self) -> int:
        return sum(result.status == MetricStatus.PASS for result in self.case_results)

    @property
    def failed_cases(self) -> int:
        return len(self.case_results) - self.passed_cases
