# [Vulnerability Report] evm.foundry.uups_uninitialized:openzeppelin-uups-governor

## Summary
- **Vulnerability Type:** `evm.foundry.uups_uninitialized`
- **Affected Location:** `contracts/proxy/utils/UUPSUpgradeable.sol:58`
- **CVE Reference(s):** `CVE-2021-41264, CVE-2021-46320, CVE-2022-31198, CVE-2022-35915, CVE-2021-41264, CVE-2021-46320, CVE-2022-31198, CVE-2022-35915`
- **Severity:** `CRITICAL`
- **Verification Status:** `verified`

## Vulnerability Details
openzeppelin-contracts — uninitialized UUPS proxy implementation allows direct initialize() + upgradeToAndCall(selfdestruct), alongside Governor historical quorum mutation and unbounded returndata copy (CVE-2021-41264, CVE-2021-46320, CVE-2022-31198, CVE-2022-35915).

## Strategy
- **Offensive memory & rule seed** — `evm.foundry.uups_uninitialized` identified the reachable entry-to-sink path in `contracts/proxy/utils/UUPSUpgradeable.sol`.
- **Attacker reachability filter** — Confirmed unauthenticated / cross-tenant exploitability under Iridium verification gates.
- **Isolated sandbox verify** — Verified in ephemeral container sandbox with deterministic oracle proof.
