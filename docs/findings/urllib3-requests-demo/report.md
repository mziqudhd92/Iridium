# [Vulnerability Report] python.sca.reachability:urllib3-requests-demo

## Summary
- **Vulnerability Type:** `python.sca.reachability`
- **Affected Location:** `app.py:10`
- **CVE Reference(s):** `CVE-2021-33503, CVE-2021-33503`
- **Severity:** `HIGH`
- **Verification Status:** `verified`

## Vulnerability Details
urllib3 < 1.26.5 (via requests 2.25.0) — HTTP route handler passes untrusted URL into requests.get(), reaching urllib3 parse_url() catastrophic backtracking sink (CVE-2021-33503).

## Strategy
- **Offensive memory & rule seed** — `python.sca.reachability` identified the reachable entry-to-sink path in `app.py`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
