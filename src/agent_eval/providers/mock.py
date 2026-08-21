from __future__ import annotations

from typing import Any

from agent_eval.providers.protocol import JudgeResult


class MockJudgeProvider:
    """Stable judge used in CI; it never calls a model or fabricates a stochastic score."""

    name = "mock"
    model = "deterministic-judge-v1"

    def __init__(self, fixed_result: JudgeResult | None = None) -> None:
        self.fixed_result = fixed_result

    async def judge(self, prompt: str, payload: dict[str, Any]) -> JudgeResult:
        if self.fixed_result is not None:
            return self.fixed_result
        required = payload.get("required_elements", [])
        response = str(payload.get("response", "")).casefold()
        present = sum(str(element).casefold() in response for element in required)
        score = 1.0 if not required else present / len(required)
        return JudgeResult(
            score=score,
            passed=score >= 0.8,
            rationale=f"deterministic presence check: {present}/{len(required)} elements",
        )
