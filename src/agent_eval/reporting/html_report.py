from __future__ import annotations

import html
from pathlib import Path

from agent_eval.models.result import EvaluationRun


def write_html_report(run: EvaluationRun, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    metric_rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{score:.1%}</td></tr>"
        for name, score in sorted(run.metrics.items())
    )
    failed_rows = (
        "".join(
            "<tr>"
            f"<td>{html.escape(case.case_id)}</td>"
            f"<td>{html.escape(case.description)}</td>"
            f"<td>{html.escape(', '.join(failure.code.value for failure in case.failures))}</td>"
            "</tr>"
            for case in run.case_results
            if case.failures
        )
        or '<tr><td colspan="3">No failed cases</td></tr>'
    )
    gate = run.gate.status.value if run.gate else "NOT_EVALUATED"
    gate_class = "pass" if gate == "PASS" else "fail"
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>AI Agent Evaluation Report</title><style>
body{{font:16px system-ui;margin:0;background:#f5f7fb;color:#172033}}main{{max-width:1100px;margin:auto;padding:32px}}
.card{{background:white;border-radius:12px;padding:22px;margin:16px 0;box-shadow:0 3px 18px #14213d18}}
.summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}
.value{{font-size:1.7rem;font-weight:700}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #e5e7eb;text-align:left}}
.pass{{color:#08783d}}.fail{{color:#b42318}}code{{font-size:.85rem}}</style></head>
<body><main><h1>AI Agent Evaluation</h1><p><code>{html.escape(run.run_id)}</code></p>
<section class="summary"><div class="card"><div>Cases</div><div class="value">{len(run.case_results)}</div></div>
<div class="card"><div>Passed</div><div class="value pass">{run.passed_cases}</div></div>
<div class="card"><div>Failed</div><div class="value fail">{run.failed_cases}</div></div>
<div class="card"><div>Quality gate</div><div class="value {gate_class}">{gate}</div></div></section>
<section class="card"><h2>Metric summary</h2><table><thead><tr><th>Metric</th><th>Score</th></tr></thead><tbody>{metric_rows}</tbody></table></section>
<section class="card"><h2>Performance</h2><p>p50 {run.percentiles_ms.get("p50", 0):.1f}ms · p95 {run.percentiles_ms.get("p95", 0):.1f}ms · p99 {run.percentiles_ms.get("p99", 0):.1f}ms</p></section>
<section class="card"><h2>Failed cases</h2><table><thead><tr><th>Case</th><th>Description</th><th>Reason codes</th></tr></thead><tbody>{failed_rows}</tbody></table></section>
<section class="card"><h2>Reproducibility</h2><pre>{html.escape(run.reproducibility.model_dump_json(indent=2))}</pre></section>
</main></body></html>"""
    destination.write_text(document, encoding="utf-8")
    return destination
