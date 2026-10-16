# [Vulnerability Report] wp.automator.dynamic_action:comboblocks-dynamic-action

## Summary
- **Vulnerability Type:** `wp.automator.dynamic_action`
- **Affected Location:** `Inc/Core/FB/Track.php:63`
- **CVE Reference(s):** `CVE-2024-11080, CVE-2024-11080`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
post-grid / firebox — REST form handler dispatches attacker-controlled JSON action names into do_action() without capability checks (CVE-2024-11080, finding 45000, JOB-BEE076).

## Strategy
- **Offensive memory & rule seed** — `wp.automator.dynamic_action` identified the reachable entry-to-sink path in `Inc/Core/FB/Track.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
