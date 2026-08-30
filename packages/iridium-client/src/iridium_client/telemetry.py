"""Product analytics opt-in helpers (off by default)."""

from __future__ import annotations

import os


def telemetry_enabled(*, cli_opt_in: bool = False, cli_opt_out: bool = False) -> bool:
    """Return whether anonymized product analytics pings may be sent."""
    if os.environ.get("DO_NOT_TRACK") == "1" or cli_opt_out:
        return False
    if cli_opt_in:
        return True
    return os.environ.get("IRIDIUM_TELEMETRY", "0").strip().lower() in ("1", "true", "yes")


def apply_telemetry_env(*, cli_opt_in: bool = False, cli_opt_out: bool = False) -> bool:
    """Resolve telemetry preference and mirror it to IRIDIUM_TELEMETRY for subprocesses."""
    enabled = telemetry_enabled(cli_opt_in=cli_opt_in, cli_opt_out=cli_opt_out)
    os.environ["IRIDIUM_TELEMETRY"] = "1" if enabled else "0"
    return enabled
