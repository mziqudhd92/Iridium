# [Vulnerability Report] python.toctou.insecure_cache_dir

## Summary
- **Vulnerability Type:** `python.toctou.insecure_cache_dir`
- **Affected Location:** `llama-index-core/llama_index/core/utils.py:419`
- **CVSS 4.0 Score:** 5.6 (MEDIUM) `CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
`get_cache_dir()` uses a predictable shared `/tmp/llama_index` path without `tempfile.mkdtemp` isolation. Hardcoded exists-then-makedirs allows symlink pre-creation and cache poisoning on multi-user Linux hosts (CVE-2025-7647). Verified on run-llama/llama_index @ v0.12.44 (finding 16110, JOB-8F5BD8).

## Strategy
- **Targeted-research rule** — `python.toctou.insecure_cache_dir` flagged `get_cache_dir()` using a predictable shared `/tmp` path.
- **Curated CVE regression** — CVE-2025-7647 package from Iridium e2e on pinned llama_index @ v0.12.44.
- **Symlink pre-creation hypothesis** — Attacker plants `/tmp/llama_index` as a symlink before `makedirs`; cache writes land in attacker-controlled directory.
- **Isolated subprocess PoC** — Child process extracts `get_cache_dir` via AST and proves attacker write through the symlinked cache dir.
- **Hunter-verify** — Proof marker written at `/tmp/iridium_proof` under Docker with `IRIDIUM_PROOF_CREATED`.
