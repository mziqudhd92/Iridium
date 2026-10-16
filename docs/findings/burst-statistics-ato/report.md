# [Vulnerability Report] wp.auth.app_password_null_bypass:burst-statistics-ato

## Summary
- **Vulnerability Type:** `wp.auth.app_password_null_bypass`
- **Affected Location:** `includes/Admin/App_Auth.php:64`
- **CVE Reference(s):** `CVE-2026-8181, CVE-2026-8181`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
burst-statistics — wp_authenticate_application_password() null return is treated as authenticated administrator during REST/Basic Auth requests (CVE-2026-8181, finding 182702).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.app_password_null_bypass` identified the reachable entry-to-sink path in `includes/Admin/App_Auth.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
