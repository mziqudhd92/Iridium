"""Tests for pre-AST secret scrubbing."""

from iridium_core.sanitize.scrubber import REDACTED, scrub_source


def test_scrubs_pem_jwt_and_api_keys() -> None:
    source = """
API_KEY = "fake_test_secret_key_32chars_long"
token = eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA
-----END RSA PRIVATE KEY-----
"""
    scrubbed = scrub_source(source)
    assert REDACTED in scrubbed
    assert "fake_test_secret_key" not in scrubbed
    assert "BEGIN RSA PRIVATE KEY" not in scrubbed
    assert "eyJhbGci" not in scrubbed


def test_preserves_low_entropy_literals() -> None:
    source = 'message = "hello-world-short-literal"\n'
    assert scrub_source(source) == source
