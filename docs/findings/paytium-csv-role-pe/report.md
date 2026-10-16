# [Vulnerability Report] wp.user.role_assignment:paytium-csv-role-pe

## Summary
- **Vulnerability Type:** `wp.user.role_assignment`
- **Affected Location:** `includes/process-payment-functions.php:174`
- **CVE Reference(s):** `CVE-2026-56030, CVE-2026-86583, CVE-2026-4283, CVE-2025-14975, CVE-2026-8809, CVE-2026-56030, CVE-2026-86583, CVE-2026-4283, CVE-2025-14975, CVE-2026-8809`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
paytium / import-users-from-csv — attacker-controlled form meta keys and CSV import columns overwrite wp_capabilities / user_email to escalate to administrator (CVE-2026-56030, CVE-2026-86583, CVE-2026-4283, CVE-2025-14975, CVE-2026-8809, finding 129199).

## Strategy
- **Offensive memory & rule seed** — `wp.user.role_assignment` identified the reachable entry-to-sink path in `includes/process-payment-functions.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
