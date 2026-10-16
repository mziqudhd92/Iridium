"""Iridium MCP server (Phase 1 skeleton)."""

from __future__ import annotations

from iridium_core import resolve_package_version


def _resolve_version() -> str:
    return resolve_package_version("iridium-mcp-server", __file__)


__version__ = _resolve_version()
