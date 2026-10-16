# [Vulnerability Report] wp.xss.second_order:ht-contactform-xss-bac

## Summary
- **Vulnerability Type:** `wp.xss.second_order`
- **Affected Location:** `include/class.ht-contactform.php:95`
- **CVE Reference(s):** `CVE-2026-96326, CVE-2026-8206, CVE-2026-83627, CVE-2026-84219, CVE-2026-96326, CVE-2026-8206, CVE-2026-83627, CVE-2026-84219`
- **Severity:** `HIGH`
- **Verification Status:** `verified`

## Vulnerability Details
ht-contactform — unauthenticated form submission and cookie-key iteration persist unsanitized payloads rendered in admin SPA views and password-reset flows (CVE-2026-96326, CVE-2026-8206, CVE-2026-83627, CVE-2026-84219, finding 161000).

## Strategy
- **Offensive memory & rule seed** — `wp.xss.second_order` identified the reachable entry-to-sink path in `include/class.ht-contactform.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
