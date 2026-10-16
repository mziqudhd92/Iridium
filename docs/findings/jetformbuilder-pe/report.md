# [Vulnerability Report] wp.user.role_assignment:jetformbuilder-pe

## Summary
- **Vulnerability Type:** `wp.user.role_assignment`
- **Affected Location:** `includes/form-handler.php:112`
- **CVE Reference(s):** `CVE-2026-12793, CVE-2026-18432, CVE-2026-62062, CVE-2026-12793, CVE-2026-18432, CVE-2026-62062`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
jetformbuilder — unauthenticated form submission with attacker-controlled _jet_engine_booking_form_id loads arbitrary post schema and mutates user roles/capabilities (CVE-2026-12793, CVE-2026-18432, CVE-2026-62062, finding 88482, JOB-959E85).

## Strategy
- **Offensive memory & rule seed** — `wp.user.role_assignment` identified the reachable entry-to-sink path in `includes/form-handler.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
