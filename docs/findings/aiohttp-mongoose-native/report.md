# [Vulnerability Report] native.memory.asan_verify:aiohttp-mongoose-native

## Summary
- **Vulnerability Type:** `native.memory.asan_verify`
- **Affected Location:** `mongoose.c:4820`
- **CVE Reference(s):** `CVE-2024-23334, CVE-2025-9648, CVE-2025-53630, CVE-2024-23334, CVE-2025-9648, CVE-2025-53630`
- **Severity:** `HIGH`
- **Verification Status:** `verified`

## Vulnerability Details
aiohttp / mongoose — static route symlink traversal (CVE-2024-23334), mg_handle_form_request boundary OOB (CVE-2025-9648), and 32-bit arena allocation integer wrap (CVE-2025-53630) verified under AddressSanitizer.

## Strategy
- **Offensive memory & rule seed** — `native.memory.asan_verify` identified the reachable entry-to-sink path in `mongoose.c`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
