"""Embedded vulnerable micro-target for demo command."""

from __future__ import annotations

import tempfile
from pathlib import Path

DEMO_APP = '''\
"""Embedded demo target — intentionally vulnerable Flask-style handler."""
import requests

def fetch_url(url: str) -> str:
    """Fetch remote content (pinned requests==2.25.0 has known CVEs)."""
    response = requests.get(url, timeout=5)
    return response.text

# Simulated HTTP route entrypoint
def handler():
  return fetch_url("https://example.com")
'''

DEMO_REQUIREMENTS = "requests==2.25.0\nflask==2.0.0\n"


def materialize_demo_target() -> Path:
    """Write embedded demo target to a temp directory."""
    tmp = Path(tempfile.mkdtemp(prefix="iridium-demo-"))
    (tmp / "app.py").write_text(DEMO_APP, encoding="utf-8")
    (tmp / "requirements.txt").write_text(DEMO_REQUIREMENTS, encoding="utf-8")
    return tmp
