# [Vulnerability Report] wp.auth.loose_otp_compare:user-verification-otp

## Summary
- **Vulnerability Type:** `wp.auth.loose_otp_compare`
- **Affected Location:** `includes/functions-otp.php:98`
- **CVE Reference(s):** `CVE-2026-7458, CVE-2026-7458`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
user-verification — loose != comparison between stored OTP meta and JSON boolean true allows unauthenticated account takeover (CVE-2026-7458, finding 182705).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.loose_otp_compare` identified the reachable entry-to-sink path in `includes/functions-otp.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
