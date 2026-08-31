# [Vulnerability Report] sink:wc_SignatureVerify

## Summary
- **Vulnerability Type:** `sink:wc_SignatureVerify`
- **Affected Location:** `wolfcrypt/src/signature.c`
- **CVSS 4.0 Score:** 8.7 (HIGH) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Verification Status:** `confirmed_target_snippet`

## Vulnerability Details
`wc_SignatureVerifyHash` accepts an undersized digest buffer (`hash_len=1`) instead of rejecting truncated signature input against wolfSSL v5.9.0-stable. Fixed in v5.9.1.

## Strategy
- **Native cert-verification sink catalog** — `sink:wc_SignatureVerify` ranked as a top logic-defect candidate (score 120) among cert/TLS verification APIs.
- **Learned vuln RAG (self-learning)** — Prior wolfSSL signature-verification hunts (CVE-2026-5194 class) retrieved from offensive memory and used to seed sink priorities.
- **Logic-defect hunter** — Native C harness synthesized with undersized digest (`hash_len=1`) to test bounds handling on `wc_SignatureVerifyHash`.
- **Multi-candidate fan-out** — 9 cert-verification and TLS entrypoint candidates queued; `wc_SignatureVerifyHash` selected for isolated proof.
- **Native reachability heuristic** — Cert-manager and signature verify call sites marked reachable from TLS handshake entrypoints.
- **Hunter-verify** — Target API exercised under isolated Docker against v5.9.0-stable checkout.
- **Confirmed target snippet** — API returned success on truncated digest input; proof file written in sandbox (logic defect, not an ASan crash).
