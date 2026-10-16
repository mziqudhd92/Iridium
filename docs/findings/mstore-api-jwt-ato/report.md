# [Vulnerability Report] wp.auth.jwt_forged_claim:mstore-api-jwt-ato

## Summary
- **Vulnerability Type:** `wp.auth.jwt_forged_claim`
- **Affected Location:** `controllers/flutter-user.php:240`
- **CVE Reference(s):** `CVE-2026-13447, CVE-2026-12492, CVE-2026-77002, CVE-2026-10580, CVE-2026-13447, CVE-2026-12492, CVE-2026-77002, CVE-2026-10580`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
mstore-api — mobile checkout/login endpoints trust unverified JWT/OTP identity claims in raw JSON POST bodies to issue administrator sessions (CVE-2026-13447, CVE-2026-12492, CVE-2026-77002, CVE-2026-10580).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.jwt_forged_claim` identified the reachable entry-to-sink path in `controllers/flutter-user.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
