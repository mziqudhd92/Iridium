# [Vulnerability Report] wp.idor.order_tracking:yith-order-tracking-idor

## Summary
- **Vulnerability Type:** `wp.idor.order_tracking`
- **Affected Location:** `init.php:132`
- **CVE Reference(s):** `CVE-2022-4019, CVE-2023-6401, CVE-2026-18442, CVE-2022-4019, CVE-2023-6401, CVE-2026-18442`
- **Severity:** `HIGH`
- **Verification Status:** `verified`

## Vulnerability Details
yith-woocommerce-order-tracking — missing order ownership verification exposes customer PII and chains with unvalidated redirect targets (CVE-2022-4019, CVE-2023-6401, CVE-2026-18442, finding 27043, JOB-532F4C).

## Strategy
- **Offensive memory & rule seed** — `wp.idor.order_tracking` identified the reachable entry-to-sink path in `init.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
