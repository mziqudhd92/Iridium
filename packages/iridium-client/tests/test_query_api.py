"""Tests for query API fail-open behavior on iridium-client."""

from unittest.mock import MagicMock, patch

from iridium_client.api.client import IridiumApiClient


def test_validate_dependency_fail_open_on_error() -> None:
    with patch("iridium_client.api.client.httpx.Client") as client_cls:
        client = MagicMock()
        client_cls.return_value.__enter__.return_value = client
        client.post.side_effect = RuntimeError("network down")
        api = IridiumApiClient(api_url="https://api.example.com")
        result = api.validate_dependency({"package": "requests", "version": "2.25.0"})
        assert result["allowed"] is True
        assert result["degraded"] is True


def test_reachability_context_fail_open_on_429() -> None:
    with patch("iridium_client.api.client.httpx.Client") as client_cls:
        client = MagicMock()
        client_cls.return_value.__enter__.return_value = client
        response = MagicMock()
        response.status_code = 429
        client.post.return_value = response
        api = IridiumApiClient(api_url="https://api.example.com")
        result = api.reachability_context({"package": "requests", "symbol": "requests.get"})
        assert result["degraded"] is True
        assert result["entrypoints"] == []
