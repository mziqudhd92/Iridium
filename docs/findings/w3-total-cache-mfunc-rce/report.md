# [Vulnerability Report] wp.rce.mfunc_eval:w3-total-cache-mfunc-rce

## Summary
- **Vulnerability Type:** `wp.rce.mfunc_eval`
- **Affected Location:** `PgCache_ContentGrabber.php:1180`
- **CVE Reference(s):** `CVE-2026-27384, CVE-2026-27384`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
w3-total-cache — page-cache dynamic fragment parser evaluates mfunc comment blocks containing attacker-controlled PHP expressions (CVE-2026-27384, finding 181455).

## Strategy
- **Offensive memory & rule seed** — `wp.rce.mfunc_eval` identified the reachable entry-to-sink path in `PgCache_ContentGrabber.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
