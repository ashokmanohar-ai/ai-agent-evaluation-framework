from __future__ import annotations

from agent_eval.models.result import EvaluationRun


def render_console(run: EvaluationRun) -> str:
    gate = run.gate.status if run.gate else "NOT_EVALUATED"
    lines = [
        "AI AGENT EVALUATION",
        "",
        f"Run: {run.run_id}",
        f"Agent: {run.agent_name} {run.agent_version}",
        f"Dataset version: {run.dataset_version}",
        f"Cases: {len(run.case_results)}",
        f"Passed: {run.passed_cases}",
        f"Failed: {run.failed_cases}",
        "",
        "METRICS",
    ]
    for name, value in sorted(run.metrics.items()):
        lines.append(f"{name:<32} {value:>7.1%}")
    lines.extend(
        [
            "",
            f"Latency p95: {run.percentiles_ms.get('p95', 0.0):.1f}ms",
            f"Behavioural stability: {(run.stability or 0.0):.1%}",
            f"Quality gate: {gate}",
        ]
    )
    if run.failure_summary:
        lines.extend(["", "TOP FAILURE CATEGORIES"])
        for code, count in run.failure_summary.items():
            lines.append(f"{code:<32} {count}")
    return "\n".join(lines)
