from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from agent_eval.core.factory import build_default_runner
from agent_eval.models.dataset import load_dataset, validate_tool_references
from agent_eval.models.enums import GateStatus
from agent_eval.policies.loader import load_tool_policy, load_yaml
from agent_eval.regression.baseline import create_baseline, load_baseline, save_baseline
from agent_eval.regression.comparator import compare_baseline
from agent_eval.reporting.console import render_console
from agent_eval.reporting.html_report import write_html_report
from agent_eval.reporting.json_report import load_json_report
from agent_eval.reporting.junit import write_junit_report
from agent_eval.reporting.writer import write_all_reports

app = typer.Typer(
    name="agent-eval",
    help="Evaluate complete AI-agent trajectories with deterministic-first quality gates.",
    no_args_is_help=True,
)
baseline_app = typer.Typer(help="Create and compare versioned evaluation baselines.")
app.add_typer(baseline_app, name="baseline")


@app.command("run")
def run_command(
    dataset: Annotated[
        list[Path] | None,
        typer.Option("--dataset", "-d", help="JSONL dataset; repeat for multiple files."),
    ] = None,
    agent: Annotated[str, typer.Option(help="Registered agent adapter.")] = "mock",
    tag: Annotated[
        list[str] | None, typer.Option("--tag", help="Run cases matching a tag.")
    ] = None,
    provider: Annotated[str, typer.Option(help="Judge provider.")] = "mock",
    runs_per_case: Annotated[int, typer.Option(min=1, max=20)] = 1,
    report_dir: Annotated[Path, typer.Option()] = Path("reports"),
    quality_gates: Annotated[Path, typer.Option()] = Path("config/quality-gates.yaml"),
    tool_policy: Annotated[Path, typer.Option()] = Path("config/tool-policy.yaml"),
) -> None:
    """Run evaluation, apply gates and emit console, JSON, HTML and JUnit reports."""
    if agent != "mock":
        raise typer.BadParameter(
            "this distribution registers 'mock'; integrate others via AgentAdapter"
        )
    paths = dataset or [Path("datasets/support/support-v1.jsonl")]
    evaluation_dataset = load_dataset(paths)
    validate_tool_references(evaluation_dataset, set(load_tool_policy(tool_policy)))
    runner = build_default_runner(
        quality_gate_path=quality_gates,
        tool_policy_path=tool_policy,
        provider_name=provider,
    )
    result = asyncio.run(
        runner.run(
            evaluation_dataset,
            tags=set(tag or []),
            runs_per_case=runs_per_case,
        )
    )
    write_all_reports(result, report_dir)
    typer.echo(render_console(result))
    if result.gate and result.gate.status == GateStatus.FAIL:
        raise typer.Exit(code=1)


@baseline_app.command("create")
def baseline_create_command(
    report: Annotated[Path, typer.Option()] = Path("reports/evaluation-report.json"),
    output: Annotated[Path, typer.Option()] = Path("baselines/mock-baseline.json"),
) -> None:
    """Create a baseline from a real evaluation report; never invent metrics."""
    run = load_json_report(report)
    destination = save_baseline(create_baseline(run), output)
    typer.echo(f"Baseline created: {destination}")


@baseline_app.command("compare")
def baseline_compare_command(
    report: Annotated[Path, typer.Option()] = Path("reports/evaluation-report.json"),
    baseline: Annotated[Path, typer.Option()] = Path("baselines/mock-baseline.json"),
    thresholds: Annotated[Path, typer.Option()] = Path("config/regression.yaml"),
) -> None:
    """Compare a current report with a compatible baseline and enforce regression limits."""
    decision = compare_baseline(
        load_baseline(baseline),
        load_json_report(report),
        load_yaml(thresholds),
    )
    typer.echo("AGENT REGRESSION")
    for check in decision.checks:
        typer.echo(
            f"{check.metric:<30} baseline={check.baseline:.1%} current={check.current:.1%} "
            f"drop={check.drop:.1%} allowed={check.allowed_drop:.1%} {check.status}"
        )
    for warning in decision.warnings:
        typer.echo(f"WARNING: {warning}")
    typer.echo(f"FINAL: {decision.status}")
    if decision.status == GateStatus.FAIL:
        raise typer.Exit(code=1)


@app.command("report")
def report_command(
    source: Annotated[Path, typer.Option()] = Path("reports/evaluation-report.json"),
    report_dir: Annotated[Path, typer.Option()] = Path("reports"),
) -> None:
    """Regenerate human-readable and CI reports from the machine-readable source report."""
    run = load_json_report(source)
    html_path = write_html_report(run, report_dir / "evaluation-report.html")
    junit_path = write_junit_report(run, report_dir / "evaluation-junit.xml")
    typer.echo(render_console(run))
    typer.echo(f"HTML: {html_path}")
    typer.echo(f"JUnit: {junit_path}")


if __name__ == "__main__":
    app()
