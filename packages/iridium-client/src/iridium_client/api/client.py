"""HTTP client for Iridium SaaS API."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from iridium_client import __version__

DEFAULT_API_URL = "https://api.iridium.example.com"
CLIENT_VERSION = __version__
POLL_INTERVAL_SECONDS = 2.0
MAX_POLL_SECONDS = 300.0
REQUEST_TIMEOUT = 30.0
QUERY_TIMEOUT = 2.0

_DEGRADED_VALIDATE = {
    "allowed": True,
    "degraded": True,
    "warning": "Iridium rate-limit reached; proceeding without reachability gate",
}
_DEGRADED_CONTEXT = {
    "entrypoints": [],
    "call_path_compressed": [],
    "call_path_full": [],
    "rewrite_hints": [],
    "secure_interface_stub": "",
    "secure_interface_docstring": "",
    "patch_available": False,
    "patch_registry_hit": False,
    "degraded": True,
    "warning": "Iridium API unavailable; proceeding without reachability context",
}


class IridiumApiClient:
    """Thin client for /api/v1/client/* endpoints."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: float = REQUEST_TIMEOUT,
    ) -> None:
        self.api_url = (api_url or os.environ.get("IRIDIUM_API_URL") or DEFAULT_API_URL).rstrip("/")
        self.api_key = api_key or os.environ.get("IRIDIUM_API_KEY")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-Iridium-Client-Version": CLIENT_VERSION,
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def submit_scan(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/client/scan — returns 202 with scan_id."""
        url = f"{self.api_url}/api/v1/client/scan"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def poll_scan(self, scan_id: str) -> dict[str, Any]:
        """GET /api/v1/client/scan/{scan_id}."""
        url = f"{self.api_url}/api/v1/client/scan/{scan_id}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def wait_for_scan(
        self,
        scan_id: str,
        *,
        poll_interval: float = POLL_INTERVAL_SECONDS,
        max_wait: float = MAX_POLL_SECONDS,
    ) -> dict[str, Any]:
        """Poll until scan completes or times out."""
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            result = self.poll_scan(scan_id)
            status = result.get("status", "").lower()
            if status in ("completed", "failed", "error"):
                return result
            time.sleep(poll_interval)
        raise TimeoutError(f"scan {scan_id} did not complete within {max_wait}s")

    def validate_dependency(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/client/query/validate-dependency (sync, <2s). Fail-open on errors."""
        url = f"{self.api_url}/api/v1/client/query/validate-dependency"
        try:
            with httpx.Client(timeout=QUERY_TIMEOUT) as client:
                response = client.post(url, json=payload, headers=self._headers())
                if response.status_code == 429:
                    return dict(_DEGRADED_VALIDATE)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            return {**_DEGRADED_VALIDATE, "warning": f"Iridium API error: {exc}"}

    def reachability_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/client/query/reachability-context (sync, <2s). Fail-open on errors."""
        url = f"{self.api_url}/api/v1/client/query/reachability-context"
        try:
            with httpx.Client(timeout=QUERY_TIMEOUT) as client:
                response = client.post(url, json=payload, headers=self._headers())
                if response.status_code == 429:
                    return dict(_DEGRADED_CONTEXT)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            return {**_DEGRADED_CONTEXT, "warning": f"Iridium API error: {exc}"}
