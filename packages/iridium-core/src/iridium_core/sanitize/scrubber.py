"""Pre-AST secret scrubbing."""

from __future__ import annotations

import re

PEM_RE = re.compile(
    r'("""|\'\'\'|[\'"]?)'
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?"
    r"-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    r"\1"
)
JWT_RE = re.compile(r'("""|\'\'\'|[\'"]?)eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\1')
API_KEY_RE = re.compile(
    r"(\b(?:api[_-]?key|secret[_-]?key|aws[_-]?secret|token)\s*[:=]\s*)"
    r'("""|\'\'\'|[\'"]?)[A-Za-z0-9_\-]{16,}\2',
    re.IGNORECASE,
)
HIGH_ENTROPY_RE = re.compile(r"['\"]([A-Za-z0-9+/=]{32,})['\"]")

REDACTED = "[REDACTED]"


def scrub_source(source: str) -> str:
    """Remove secrets and high-entropy literals before AST parsing while preserving syntax."""

    def _pem_replace(match: re.Match[str]) -> str:
        quote = match.group(1) or '"'
        newlines = "\n" * match.group(0).count("\n")
        return f"{quote}{REDACTED}{newlines}{quote}"

    def _jwt_replace(match: re.Match[str]) -> str:
        quote = match.group(1) or '"'
        return f"{quote}{REDACTED}{quote}"

    def _api_key_replace(match: re.Match[str]) -> str:
        prefix = match.group(1)
        quote = match.group(2) or '"'
        return f"{prefix}{quote}{REDACTED}{quote}"

    text = PEM_RE.sub(_pem_replace, source)
    text = JWT_RE.sub(_jwt_replace, text)
    text = API_KEY_RE.sub(_api_key_replace, text)

    def _entropy_replace(match: re.Match[str]) -> str:
        value = match.group(1)
        if _shannon_entropy(value) > 4.5:
            return f'"{REDACTED}"'
        return match.group(0)

    return HIGH_ENTROPY_RE.sub(_entropy_replace, text)


def _shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    import math
    from collections import Counter

    counts = Counter(data)
    length = len(data)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())
