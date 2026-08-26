"""Tests for terminal rendering helpers."""

from unittest.mock import patch

from iridium_client.output.terminal import (
    render_demo_graph,
    render_scan_results,
    render_zero_results,
)


def test_render_zero_results_prints_summary() -> None:
    with patch("iridium_client.output.terminal.console.print") as mock_print:
        render_zero_results(
            duration_s=1.2,
            dependency_count=3,
            entrypoint_count=2,
            languages=["python"],
            reachable_count=0,
            raw_cve_count=10,
        )
    assert mock_print.called
    panel_arg = mock_print.call_args[0][0]
    assert "Scan complete" in str(panel_arg.renderable)


def test_render_scan_results_with_reachable_findings() -> None:
    with patch("iridium_client.output.terminal.console.print") as mock_print:
        render_scan_results(
            {
                "findings": [
                    {"sca_reachable": True, "rule_id": "CVE-2024-1", "package": "requests"}
                ],
                "summary": {
                    "dependency_count": 1,
                    "entrypoint_count": 1,
                    "languages": ["python"],
                    "reachable_finding_count": 1,
                    "raw_cve_count": 3,
                },
            },
            duration_s=2.0,
        )
    assert mock_print.called


def test_render_scan_results_with_legacy_reachable_field() -> None:
    with patch("iridium_client.output.terminal.console.print") as mock_print:
        render_scan_results(
            {
                "findings": [{"reachable": True, "cve_id": "CVE-2024-1", "path": "requests.get"}],
                "dependency_count": 1,
                "entrypoint_count": 1,
                "languages": ["python"],
            },
            duration_s=2.0,
        )
    assert mock_print.called


def test_render_scan_results_falls_back_to_zero_state() -> None:
    with patch("iridium_client.output.terminal.render_zero_results") as mock_zero:
        render_scan_results({"findings": []}, duration_s=1.0)
    mock_zero.assert_called_once()


def test_render_demo_graph_prints_panel() -> None:
    with patch("iridium_client.output.terminal.console.print") as mock_print:
        render_demo_graph()
    assert mock_print.called
