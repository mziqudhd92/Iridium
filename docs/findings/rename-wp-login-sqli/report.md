# [Vulnerability Report] wp.sqli.login_failed_log:rename-wp-login-sqli

## Summary
- **Vulnerability Type:** `wp.sqli.login_failed_log`
- **Affected Location:** `rename-wp-login.php:214`
- **CVE Reference(s):** `CVE-2026-93368, CVE-2026-93368`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
rename-wp-login — failed login handler interpolates unsanitized username/header fields into an unprepared $wpdb->query INSERT on wp_login_failed (CVE-2026-93368).

## Strategy
- **Offensive memory & rule seed** — `wp.sqli.login_failed_log` identified the reachable entry-to-sink path in `rename-wp-login.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
