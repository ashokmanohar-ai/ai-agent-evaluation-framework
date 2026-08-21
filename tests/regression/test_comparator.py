from pathlib import Path

from agent_eval.core.factory import build_default_runner
from agent_eval.models.dataset import load_dataset
from agent_eval.models.enums import GateStatus
from agent_eval.policies.loader import load_yaml
from agent_eval.regression.baseline import create_baseline
from agent_eval.regression.comparator import compare_baseline


async def test_identical_run_has_no_regression() -> None:
    run = await build_default_runner().run(
        load_dataset([Path("datasets/support/support-v1.jsonl")])
    )
    decision = compare_baseline(create_baseline(run), run, load_yaml("config/regression.yaml"))
    assert decision.status == GateStatus.PASS


async def test_safety_regression_has_zero_tolerance() -> None:
    run = await build_default_runner().run(
        load_dataset([Path("datasets/support/support-v1.jsonl")])
    )
    baseline = create_baseline(run)
    baseline.metrics["safety"] = 1.0
    run.metrics["safety"] = 0.99
    decision = compare_baseline(baseline, run, load_yaml("config/regression.yaml"))
    safety = next(check for check in decision.checks if check.metric == "safety")
    assert safety.status == GateStatus.FAIL
    assert decision.status == GateStatus.FAIL
