from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent_eval.core.factory import build_default_runner
from agent_eval.models.dataset import load_dataset, validate_tool_references
from agent_eval.models.result import EvaluationRun
from agent_eval.policies.loader import load_tool_policy
from agent_eval.regression.baseline import Baseline, load_baseline

app = FastAPI(title="AI Agent Evaluation API", version="1.0.0")
_runs: dict[str, EvaluationRun] = {}


class EvaluationRequest(BaseModel):
    dataset_paths: list[str] = Field(default_factory=lambda: ["datasets/support/support-v1.jsonl"])
    tags: list[str] = Field(default_factory=list)
    runs_per_case: int = Field(default=1, ge=1, le=20)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/evaluations", response_model=EvaluationRun)
async def create_evaluation(request: EvaluationRequest) -> EvaluationRun:
    try:
        dataset = load_dataset([Path(path) for path in request.dataset_paths])
        validate_tool_references(dataset, set(load_tool_policy("config/tool-policy.yaml")))
        result = await build_default_runner().run(
            dataset,
            tags=set(request.tags),
            runs_per_case=request.runs_per_case,
        )
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _runs[result.run_id] = result
    return result


@app.get("/api/v1/evaluations/{evaluation_id}", response_model=EvaluationRun)
async def get_evaluation(evaluation_id: str) -> EvaluationRun:
    try:
        return _runs[evaluation_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="evaluation not found") from exc


@app.get("/api/v1/evaluations/{evaluation_id}/report", response_model=EvaluationRun)
async def get_evaluation_report(evaluation_id: str) -> EvaluationRun:
    return await get_evaluation(evaluation_id)


@app.get("/api/v1/baselines", response_model=list[Baseline])
async def list_baselines() -> list[Baseline]:
    paths = sorted(Path("baselines").glob("*.json"))  # noqa: ASYNC240
    return [load_baseline(path) for path in paths]
