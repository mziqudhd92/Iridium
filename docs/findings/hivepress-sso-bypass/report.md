# [Vulnerability Report] wp.auth.sso_token_bypass:hivepress-sso-bypass

## Summary
- **Vulnerability Type:** `wp.auth.sso_token_bypass`
- **Affected Location:** `includes/controllers/class-user.php:129`
- **CVE Reference(s):** `CVE-2026-18056, CVE-2026-18056`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
hivepress — REST/SSO token verification accepts predictable or empty token state and authenticates the target user (CVE-2026-18056).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.sso_token_bypass` identified the reachable entry-to-sink path in `includes/controllers/class-user.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
