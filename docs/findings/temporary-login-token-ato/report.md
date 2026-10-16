# [Vulnerability Report] wp.auth.empty_token_meta_bypass:temporary-login-token-ato

## Summary
- **Vulnerability Type:** `wp.auth.empty_token_meta_bypass`
- **Affected Location:** `includes/class-wp-temporary-login-without-password-common.php:142`
- **CVE Reference(s):** `CVE-2026-7567, CVE-2026-7567`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
temporary-login-without-password — passing wt_token[] as an array produces an empty sanitize_key() lookup that matches empty usermeta and logs in as administrator (CVE-2026-7567).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.empty_token_meta_bypass` identified the reachable entry-to-sink path in `includes/class-wp-temporary-login-without-password-common.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
