from pathlib import Path

from agent_eval.core.factory import build_default_runner
from agent_eval.models.dataset import load_dataset
from agent_eval.models.enums import GateStatus


async def test_full_seventy_case_offline_suite_passes() -> None:
    paths = sorted(Path("datasets").glob("*/*.jsonl"))  # noqa: ASYNC240
    dataset = load_dataset(paths)
    run = await build_default_runner(provider_name="mock").run(dataset)
    assert len(run.case_results) == 70
    assert run.failed_cases == 0
    assert run.gate is not None
    assert run.gate.status == GateStatus.PASS
    assert run.metrics["safety"] == 1.0
    assert run.metrics["tool_selection"] == 1.0


async def test_repeated_runs_report_stability() -> None:
    dataset = load_dataset([Path("datasets/support/support-v1.jsonl")])
    run = await build_default_runner().run(dataset, tags={"smoke"}, runs_per_case=3)
    assert run.stability == 1.0
    assert all(result.run_index in {1, 2, 3} for result in run.case_results)
