"""Background warm-index thread for MCP cold-start mitigation."""

from __future__ import annotations

import threading
from pathlib import Path

from iridium_mcp.workspace import append_audit, warm_index_workspace


def start_background_index(root: Path | None = None) -> threading.Thread:
    def _run() -> None:
        try:
            warm_index_workspace(root=root, use_process_pool=False)
            append_audit("background warm-index complete", root=root)
        except Exception as exc:
            append_audit(f"background warm-index failed: {exc}", root=root)

    thread = threading.Thread(target=_run, name="iridium-warm-index", daemon=True)
    thread.start()
    return thread
