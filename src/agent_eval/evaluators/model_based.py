from __future__ import annotations

import asyncio
import statistics
from pathlib import Path
from typing import Any

from agent_eval.core.evaluator import Evaluator
from agent_eval.evaluators.deterministic import _result
from agent_eval.models.dataset import EvaluationCase
from agent_eval.models.enums import EvaluationDimension, FailureCode
from agent_eval.models.result import Failure, MetricResult
from agent_eval.models.trace import AgentTrace
from agent_eval.providers.protocol import JudgeProvider, JudgeResult


class ResponseQualityEvaluator(Evaluator):
    name = "response_quality"

    def __init__(
        self,
        provider: JudgeProvider,
        *,
        prompt_path: str | Path = "prompts/judges/response-quality-v1.md",
        repeats: int = 1,
        timeout_seconds: float = 30.0,
    ) -> None:
        if repeats < 1:
            raise ValueError("judge repeats must be at least 1")
        self.provider = provider
        self.prompt_path = Path(prompt_path)
        self.repeats = repeats
        self.timeout_seconds = timeout_seconds

    async def evaluate(self, case: EvaluationCase, trace: AgentTrace) -> MetricResult:
        required_elements = case.metadata.get("semantic_required_elements")
        if not isinstance(required_elements, list):
            return _result(
                self.name,
                EvaluationDimension.QUALITY,
                1.0,
                "semantic response evaluation was not requested for this case",
                skipped=True,
            )
        prompt = self.prompt_path.read_text(encoding="utf-8")
        payload: dict[str, Any] = {
            "user_input": case.input,
            "response": trace.final_output,
            "required_elements": required_elements,
            "trajectory_summary": [step.name for step in trace.steps],
        }
        results: list[JudgeResult] = []
        failures: list[Failure] = []
        for _ in range(self.repeats):
            try:
                result = await asyncio.wait_for(
                    self.provider.judge(prompt, payload), timeout=self.timeout_seconds
                )
                results.append(result)
            except (TimeoutError, ValueError) as exc:
                failures.append(
                    Failure(
                        code=FailureCode.TIMEOUT,
                        message=f"judge failed safely: {exc}",
                        evidence={"provider": self.provider.name},
                    )
                )
        if not results:
            return _result(
                self.name,
                EvaluationDimension.QUALITY,
                0.0,
                "no valid judge result was produced",
                failures,
            )
        score = statistics.median(result.score for result in results)
        return _result(
            self.name,
            EvaluationDimension.QUALITY,
            score,
            f"median of {len(results)} structured judge result(s)",
            failures,
            {
                "provider": self.provider.name,
                "model": self.provider.model,
                "prompt_version": "response-quality-v1",
                "rationales": [result.rationale for result in results],
            },
        )
