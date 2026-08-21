from __future__ import annotations

from pathlib import Path

from agent_eval.models.result import EvaluationRun


def write_json_report(run: EvaluationRun, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    return destination


def load_json_report(path: str | Path) -> EvaluationRun:
    return EvaluationRun.model_validate_json(Path(path).read_text(encoding="utf-8"))
