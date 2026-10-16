# [Vulnerability Report] wp.lfi.user_include:wp-maps-lfi

## Summary
- **Vulnerability Type:** `wp.lfi.user_include`
- **Affected Location:** `core/class.controller.php:77`
- **CVE Reference(s):** `CVE-2026-16263, CVE-2026-16263`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
wp-google-map-plugin — explode('_', $_GET['page']) builds a view path without traversal canonicalization, allowing local PHP file inclusion (CVE-2026-16263, finding 135683).

## Strategy
- **Offensive memory & rule seed** — `wp.lfi.user_include` identified the reachable entry-to-sink path in `core/class.controller.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
