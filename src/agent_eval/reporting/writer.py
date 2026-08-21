from __future__ import annotations

from pathlib import Path

from agent_eval.models.result import EvaluationRun
from agent_eval.reporting.html_report import write_html_report
from agent_eval.reporting.json_report import write_json_report
from agent_eval.reporting.junit import write_junit_report


def write_all_reports(run: EvaluationRun, directory: str | Path = "reports") -> dict[str, Path]:
    target = Path(directory)
    return {
        "json": write_json_report(run, target / "evaluation-report.json"),
        "html": write_html_report(run, target / "evaluation-report.html"),
        "junit": write_junit_report(run, target / "evaluation-junit.xml"),
    }
