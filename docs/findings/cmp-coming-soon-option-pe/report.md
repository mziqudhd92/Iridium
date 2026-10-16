# [Vulnerability Report] wp.option.unconstrained_update:cmp-coming-soon-option-pe

## Summary
- **Vulnerability Type:** `wp.option.unconstrained_update`
- **Affected Location:** `niteo-cmp.php:520`
- **CVE Reference(s):** `CVE-2026-12470, CVE-2023-22695, CVE-2023-38392, CVE-2026-12470, CVE-2023-22695, CVE-2023-38392`
- **Severity:** `HIGH`
- **Verification Status:** `verified`

## Vulnerability Details
cmp-coming-soon-maintenance — AJAX settings import writes arbitrary WordPress options without administrator capability checks (CVE-2026-12470, CVE-2023-22695, CVE-2023-38392, finding 119523).

## Strategy
- **Offensive memory & rule seed** — `wp.option.unconstrained_update` identified the reachable entry-to-sink path in `niteo-cmp.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
