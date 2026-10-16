# [Vulnerability Report] wp.lfi.user_include:eventin-layout-lfi

## Summary
- **Vulnerability Type:** `wp.lfi.user_include`
- **Affected Location:** `core/event/template-functions.php:54`
- **CVE Reference(s):** `CVE-2026-84898, CVE-2026-84898`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
wp-event-solution <= 4.1.20 — stored event_layout post meta flows into include_once without template allowlist validation (CVE-2026-84898, finding 86137, JOB-58041B).

## Strategy
- **Offensive memory & rule seed** — `wp.lfi.user_include` identified the reachable entry-to-sink path in `core/event/template-functions.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
