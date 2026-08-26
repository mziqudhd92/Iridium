"""Pre-AST secret scrubbing."""

from __future__ import annotations

import re

PEM_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)
JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
API_KEY_RE = re.compile(
    r"\b(?:api[_-]?key|secret[_-]?key|aws[_-]?secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}",
    re.IGNORECASE,
)
HIGH_ENTROPY_RE = re.compile(r"['\"]([A-Za-z0-9+/=]{32,})['\"]")

REDACTED = "[REDACTED]"


def scrub_source(source: str) -> str:
    """Remove secrets and high-entropy literals before AST parsing."""
    text = PEM_RE.sub(REDACTED, source)
    text = JWT_RE.sub(REDACTED, text)
    text = API_KEY_RE.sub(lambda m: m.group(0).split("=")[0] + "= " + REDACTED, text)

    def _entropy_replace(match: re.Match[str]) -> str:
        value = match.group(1)
        if _shannon_entropy(value) > 4.5:
            return f'"{REDACTED}"'
        return match.group(0)

    return HIGH_ENTROPY_RE.sub(_entropy_replace, text)


def _shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    from collections import Counter
    import math

    counts = Counter(data)
    length = len(data)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())
