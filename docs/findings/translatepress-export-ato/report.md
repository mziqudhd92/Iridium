# [Vulnerability Report] wp.info.dictionary_export_leak:translatepress-export-ato

## Summary
- **Vulnerability Type:** `wp.info.dictionary_export_leak`
- **Affected Location:** `includes/class-translation-manager.php:310`
- **CVE Reference(s):** `CVE-2026-19632, CVE-2026-19632`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
translatepress-multilingual — unauthenticated dictionary/translation export leaks captured password-reset links and sensitive user tokens (CVE-2026-19632, finding 109241).

## Strategy
- **Offensive memory & rule seed** — `wp.info.dictionary_export_leak` identified the reachable entry-to-sink path in `includes/class-translation-manager.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
