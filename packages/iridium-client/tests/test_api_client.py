"""Tests for IridiumApiClient HTTP behavior (mocked httpx)."""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from iridium_client.api.client import IridiumApiClient


def _sample_payload() -> dict[str, object]:
    return {
        "schema_version": "1",
        "repo_fingerprint": "abcdefgh",
        "languages": ["python"],
    }


def test_submit_scan_posts_with_api_key_header() -> None:
    with patch("iridium_client.api.client.httpx.Client") as client_cls:
        client = MagicMock()
        client_cls.return_value.__enter__.return_value = client
        response = MagicMock()
        response.json.return_value = {"scan_id": "SCAN-ABC123"}
        client.post.return_value = response

        api = IridiumApiClient(api_url="https://api.example.com", api_key="secret")
        result = api.submit_scan(_sample_payload())

    assert result["scan_id"] == "SCAN-ABC123"
    _, kwargs = client.post.call_args
    assert kwargs["headers"]["X-API-Key"] == "secret"
    assert kwargs["json"]["schema_version"] == "1"


def test_poll_scan_gets_status() -> None:
    with patch("iridium_client.api.client.httpx.Client") as client_cls:
        client = MagicMock()
        client_cls.return_value.__enter__.return_value = client
        response = MagicMock()
        response.json.return_value = {"status": "COMPLETED", "findings": []}
        client.get.return_value = response

        api = IridiumApiClient(api_url="https://api.example.com")
        body = api.poll_scan("SCAN-ABC123")

    assert body["status"] == "COMPLETED"
    client.get.assert_called_once()


def test_wait_for_scan_polls_until_terminal_status() -> None:
    api = IridiumApiClient(api_url="https://api.example.com")
    with patch.object(api, "poll_scan") as poll:
        poll.side_effect = [
            {"status": "RUNNING"},
            {"status": "COMPLETED", "findings": []},
        ]
        with patch("iridium_client.api.client.time.sleep"):
            result = api.wait_for_scan("SCAN-ABC123", poll_interval=0.01, max_wait=5.0)
    assert result["status"] == "COMPLETED"


def test_wait_for_scan_times_out() -> None:
    api = IridiumApiClient(api_url="https://api.example.com")
    with (
        patch.object(api, "poll_scan", return_value={"status": "RUNNING"}),
        patch("iridium_client.api.client.time.monotonic", side_effect=[0.0, 0.0, 10.0]),
        pytest.raises(TimeoutError, match="did not complete"),
    ):
        api.wait_for_scan("SCAN-ABC123", poll_interval=0.01, max_wait=1.0)


def test_submit_scan_raises_on_http_error() -> None:
    with patch("iridium_client.api.client.httpx.Client") as client_cls:
        client = MagicMock()
        client_cls.return_value.__enter__.return_value = client
        response = MagicMock()
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "unauthorized",
            request=MagicMock(),
            response=MagicMock(status_code=401),
        )
        client.post.return_value = response

        api = IridiumApiClient(api_url="https://api.example.com", api_key="bad")
        with pytest.raises(httpx.HTTPStatusError):
            api.submit_scan(_sample_payload())
