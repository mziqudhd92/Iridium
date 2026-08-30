"""HTTP client for sync query endpoints with fail-open semantics."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_URL = "https://api.iridium.example.com"
CLIENT_VERSION = "0.5.0"
REQUEST_TIMEOUT = 2.0

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


class QueryApiClient:
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

    def validate_dependency(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_url}/api/v1/client/query/validate-dependency"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=self._headers())
                if response.status_code == 429:
                    return dict(_DEGRADED_VALIDATE)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            return {**_DEGRADED_VALIDATE, "warning": f"Iridium API error: {exc}"}

    def reachability_context(self, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_url}/api/v1/client/query/reachability-context"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=self._headers())
                if response.status_code == 429:
                    return dict(_DEGRADED_CONTEXT)
                response.raise_for_status()
                return response.json()
        except Exception as exc:
            return {**_DEGRADED_CONTEXT, "warning": f"Iridium API error: {exc}"}
