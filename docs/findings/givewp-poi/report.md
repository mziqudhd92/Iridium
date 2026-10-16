# [Vulnerability Report] wp.deserial.unserialize:givewp-poi

## Summary
- **Vulnerability Type:** `wp.deserial.unserialize`
- **Affected Location:** `includes/process-donation.php:185`
- **CVE Reference(s):** `CVE-2024-5932, CVE-2026-82222, CVE-2024-5932, CVE-2026-82222`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
give <= 3.14.1 — unauthenticated donation form submission and purchase-session handling pass attacker-controlled serialized objects into unserialize() (CVE-2024-5932, CVE-2026-82222).

## Strategy
- **Offensive memory & rule seed** — `wp.deserial.unserialize` identified the reachable entry-to-sink path in `includes/process-donation.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
