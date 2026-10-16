# [Vulnerability Report] wp.fs.arbitrary_upload:woocommerce-delivery-notes-rce

## Summary
- **Vulnerability Type:** `wp.fs.arbitrary_upload`
- **Affected Location:** `includes/class-wcdn-print.php:89`
- **CVE Reference(s):** `CVE-2025-13773, CVE-2026-40746, CVE-2026-42737, CVE-2025-7852, CVE-2023-4596, CVE-2025-13773, CVE-2026-40746, CVE-2026-42737, CVE-2025-7852, CVE-2023-4596`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
woocommerce-delivery-notes — guest order-print / upload endpoints permit arbitrary file write or Dompdf PHP evaluation before extension validation (CVE-2025-13773, CVE-2026-40746, CVE-2026-42737, CVE-2025-7852, CVE-2023-4596).

## Strategy
- **Offensive memory & rule seed** — `wp.fs.arbitrary_upload` identified the reachable entry-to-sink path in `includes/class-wcdn-print.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
