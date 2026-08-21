from pathlib import Path

from httpx import ASGITransport, AsyncClient
from typer.testing import CliRunner

from agent_eval.api.app import app as api_app
from agent_eval.cli.main import app


def test_cli_smoke_run_writes_all_reports(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "run",
            "--dataset",
            "datasets/support/support-v1.jsonl",
            "--tag",
            "smoke",
            "--report-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "evaluation-report.json").exists()
    assert (tmp_path / "evaluation-report.html").exists()
    assert (tmp_path / "evaluation-junit.xml").exists()


async def test_api_health() -> None:
    async with AsyncClient(transport=ASGITransport(app=api_app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
