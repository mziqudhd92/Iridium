"""Telemetry opt-in tests."""

import os

from iridium_client.telemetry import apply_telemetry_env, telemetry_enabled


def test_telemetry_off_by_default(monkeypatch) -> None:
    monkeypatch.delenv("IRIDIUM_TELEMETRY", raising=False)
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    assert telemetry_enabled() is False


def test_telemetry_cli_opt_in(monkeypatch) -> None:
    monkeypatch.delenv("IRIDIUM_TELEMETRY", raising=False)
    assert telemetry_enabled(cli_opt_in=True) is True


def test_telemetry_env_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("IRIDIUM_TELEMETRY", "1")
    assert telemetry_enabled() is True


def test_telemetry_do_not_track_wins(monkeypatch) -> None:
    monkeypatch.setenv("IRIDIUM_TELEMETRY", "1")
    monkeypatch.setenv("DO_NOT_TRACK", "1")
    assert telemetry_enabled(cli_opt_in=True) is False


def test_telemetry_cli_opt_out_overrides_env(monkeypatch) -> None:
    monkeypatch.setenv("IRIDIUM_TELEMETRY", "1")
    assert telemetry_enabled(cli_opt_out=True) is False


def test_apply_telemetry_env_sets_flag(monkeypatch) -> None:
    monkeypatch.delenv("IRIDIUM_TELEMETRY", raising=False)
    apply_telemetry_env(cli_opt_in=True)
    assert os.environ["IRIDIUM_TELEMETRY"] == "1"
    monkeypatch.delenv("IRIDIUM_TELEMETRY", raising=False)
    apply_telemetry_env()
    assert os.environ["IRIDIUM_TELEMETRY"] == "0"
