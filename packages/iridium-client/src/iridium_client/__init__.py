"""Iridium CLI — local scanning and SaaS upload."""

from __future__ import annotations

from iridium_core import resolve_package_version


def _resolve_version() -> str:
    return resolve_package_version("iridium-client", __file__)


__version__ = _resolve_version()
