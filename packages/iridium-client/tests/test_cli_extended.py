"""Extended CLI behavior tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from iridium_client.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_scan_success_renders_results(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    with patch("iridium_client.cli.IridiumApiClient") as mock_client_cls:
        client = MagicMock()
        mock_client_cls.return_value = client
        client.submit_scan.return_value = {"scan_id": "SCAN-OK"}
        client.wait_for_scan.return_value = {
            "status": "COMPLETED",
            "findings": [{"reachable": True, "cve_id": "CVE-1", "path": "pkg"}],
        }
        result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0


def test_scan_block_on_error_exits_nonzero(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    with patch("iridium_client.cli.IridiumApiClient") as mock_client:
        mock_client.return_value.submit_scan.side_effect = ConnectionError("offline")
        result = runner.invoke(app, ["scan", str(tmp_path), "--on-error", "block"])
    assert result.exit_code == 1


def test_payload_dump_writes_output_file(tmp_path: Path) -> None:
    (tmp_path / "main.py").write_text("def f():\n    pass\n", encoding="utf-8")
    out = tmp_path / "out.json"
    result = runner.invoke(
        app,
        ["payload", "dump", str(tmp_path), "--validate", "--output", str(out)],
    )
    assert result.exit_code == 0
    assert out.is_file()
    assert '"schema_version"' in out.read_text(encoding="utf-8")
