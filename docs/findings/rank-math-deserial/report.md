# [Vulnerability Report] wp.deserial.second_order:rank-math-deserial

## Summary
- **Vulnerability Type:** `wp.deserial.second_order`
- **Affected Location:** `includes/modules/schema/class-frontend.php:145`
- **CVE Reference(s):** `CVE-2026-81757, CVE-2026-81757`
- **Severity:** `HIGH`
- **Verification Status:** `verified`

## Vulnerability Details
seo-by-rank-math — low-privilege metadata plant flows into unserialize() during frontend/admin SEO schema evaluation (CVE-2026-81757, finding 110059).

## Strategy
- **Offensive memory & rule seed** — `wp.deserial.second_order` identified the reachable entry-to-sink path in `includes/modules/schema/class-frontend.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
