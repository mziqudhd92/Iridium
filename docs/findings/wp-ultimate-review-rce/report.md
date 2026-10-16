# [Vulnerability Report] wp.rce.second_order:wp-ultimate-review-rce

## Summary
- **Vulnerability Type:** `wp.rce.second_order`
- **Affected Location:** `views/public/meta-box-user-review.php:88`
- **CVE Reference(s):** `CVE-2026-92235, CVE-2026-92235`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
wp-ultimate-review — public review submission persists unstripped shortcode tags that execute via do_shortcode() on review render (CVE-2026-92235, finding 119450).

## Strategy
- **Offensive memory & rule seed** — `wp.rce.second_order` identified the reachable entry-to-sink path in `views/public/meta-box-user-review.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
