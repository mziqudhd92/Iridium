# [Vulnerability Report] wp.auth.verify_fallthrough:ethpress-auth-bypass

## Summary
- **Vulnerability Type:** `wp.auth.verify_fallthrough`
- **Affected Location:** `app/Login.php:91`
- **CVE Reference(s):** `CVE-2026-19125, CVE-2026-19125`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
ethpress — signature verification callback falls through on malformed/empty ECDSA verification state and issues wp_set_auth_cookie for administrator (CVE-2026-19125).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.verify_fallthrough` identified the reachable entry-to-sink path in `app/Login.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
