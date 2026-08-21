from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from agent_eval.models.result import EvaluationRun


class Baseline(BaseModel):
    agent_name: str
    agent_version: str
    dataset_version: str
    framework_version: str
    evaluator_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metrics: dict[str, float]
    percentiles_ms: dict[str, float]
    source_run_id: str


def create_baseline(run: EvaluationRun) -> Baseline:
    return Baseline(
        agent_name=run.agent_name,
        agent_version=run.agent_version,
        dataset_version=run.dataset_version,
        framework_version=run.reproducibility.framework_version,
        evaluator_version=run.reproducibility.evaluator_version,
        metrics=run.metrics,
        percentiles_ms=run.percentiles_ms,
        source_run_id=run.run_id,
    )


def save_baseline(baseline: Baseline, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(baseline.model_dump_json(indent=2), encoding="utf-8")
    return destination


def load_baseline(path: str | Path) -> Baseline:
    return Baseline.model_validate_json(Path(path).read_text(encoding="utf-8"))
