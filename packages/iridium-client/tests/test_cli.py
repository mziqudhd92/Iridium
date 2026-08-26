"""Basic CLI tests."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from iridium_client.cli import app

runner = CliRunner()


def test_demo_command():
    result = runner.invoke(app, ["demo"])
    assert result.exit_code == 0
    assert "Reachability graph" in result.stdout or "demo" in result.stdout.lower()


def test_payload_dump_validate(tmp_path: Path):
    (tmp_path / "main.py").write_text("def hello():\n    pass\n", encoding="utf-8")
    result = runner.invoke(app, ["payload", "dump", str(tmp_path), "--validate"])
    assert result.exit_code == 0
    assert "schema_version" in result.stdout or "validated" in result.stdout.lower()


def test_scan_on_error_pass(tmp_path: Path):
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    with patch("iridium_client.cli.IridiumApiClient") as mock_client:
        mock_client.return_value.submit_scan.side_effect = ConnectionError("offline")
        result = runner.invoke(app, ["scan", str(tmp_path), "--on-error", "pass"])
    assert result.exit_code == 0
