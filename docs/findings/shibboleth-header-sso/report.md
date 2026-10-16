# [Vulnerability Report] wp.auth.header_sso_bypass:shibboleth-header-sso

## Summary
- **Vulnerability Type:** `wp.auth.header_sso_bypass`
- **Affected Location:** `shibboleth.php:412`
- **CVE Reference(s):** `CVE-2026-12281, CVE-2026-12281`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
shibboleth — trusts client-supplied HTTP identity headers when reverse-proxy stripping is absent, auto-provisioning or authenticating an administrator account (CVE-2026-12281, finding 140831).

## Strategy
- **Offensive memory & rule seed** — `wp.auth.header_sso_bypass` identified the reachable entry-to-sink path in `shibboleth.php`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
