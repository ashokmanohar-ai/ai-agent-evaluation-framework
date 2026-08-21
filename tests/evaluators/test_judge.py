import asyncio
from pathlib import Path
from typing import Any

from agent_eval.evaluators.model_based import ResponseQualityEvaluator
from agent_eval.models.enums import MetricStatus
from agent_eval.providers.mock import MockJudgeProvider
from agent_eval.providers.protocol import JudgeResult
from tests.helpers import make_case, make_trace


async def test_mock_judge_returns_structured_score() -> None:
    case = make_case()
    case.metadata["semantic_required_elements"] = ["ticket", "status"]
    evaluator = ResponseQualityEvaluator(MockJudgeProvider())
    result = await evaluator.evaluate(case, make_trace(final_output="The ticket status is open."))
    assert result.status == MetricStatus.PASS
    assert result.score == 1.0


async def test_repeated_judging_uses_median() -> None:
    case = make_case()
    case.metadata["semantic_required_elements"] = ["answer"]
    provider = MockJudgeProvider(JudgeResult(score=0.9, passed=True, rationale="fixed"))
    result = await ResponseQualityEvaluator(provider, repeats=3).evaluate(
        case, make_trace(final_output="answer")
    )
    assert result.score == 0.9
    assert len(result.details["rationales"]) == 3


class FailingJudge:
    name = "failing"
    model = "invalid"

    async def judge(self, prompt: str, payload: dict[str, Any]) -> JudgeResult:
        raise ValueError("malformed score")


async def test_malformed_judge_output_fails_closed() -> None:
    case = make_case()
    case.metadata["semantic_required_elements"] = ["answer"]
    result = await ResponseQualityEvaluator(FailingJudge()).evaluate(case, make_trace())
    assert result.status == MetricStatus.FAIL
    assert result.score == 0.0


class SlowJudge:
    name = "slow"
    model = "timeout"

    async def judge(self, prompt: str, payload: dict[str, Any]) -> JudgeResult:
        await asyncio.sleep(0.05)
        return JudgeResult(score=1.0, passed=True, rationale="late")


async def test_judge_timeout_fails_closed() -> None:
    case = make_case()
    case.metadata["semantic_required_elements"] = ["answer"]
    evaluator = ResponseQualityEvaluator(
        SlowJudge(),
        prompt_path=Path("prompts/judges/response-quality-v1.md"),
        timeout_seconds=0.001,
    )
    result = await evaluator.evaluate(case, make_trace())
    assert result.status == MetricStatus.FAIL
