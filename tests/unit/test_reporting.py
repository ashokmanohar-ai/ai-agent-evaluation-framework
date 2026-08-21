from pathlib import Path
from xml.etree.ElementTree import parse

from agent_eval.core.factory import build_default_runner
from agent_eval.models.dataset import load_dataset
from agent_eval.reporting.html_report import write_html_report
from agent_eval.reporting.json_report import load_json_report, write_json_report
from agent_eval.reporting.junit import write_junit_report


async def test_json_html_and_junit_reports_are_valid(tmp_path: Path) -> None:
    run = await build_default_runner().run(
        load_dataset([Path("datasets/support/support-v1.jsonl")])
    )
    json_path = write_json_report(run, tmp_path / "report.json")
    html_path = write_html_report(run, tmp_path / "report.html")
    junit_path = write_junit_report(run, tmp_path / "report.xml")
    assert load_json_report(json_path).run_id == run.run_id
    assert "AI Agent Evaluation" in html_path.read_text(encoding="utf-8")
    assert parse(junit_path).getroot().tag == "testsuite"  # noqa: S314
