# [Vulnerability Report] library-sink:requests.utils.extract_zipped_paths

## Summary
- **Vulnerability Type:** `library-sink:requests.utils.extract_zipped_paths`
- **Affected Location:** `src/requests/utils.py`
- **CVSS 4.0 Score:** 5.3 (MEDIUM) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
TOCTOU in `extract_zipped_paths`: a predictable temp member path lets an attacker plant content at the extraction target before zip membership is validated, returning attacker-controlled bytes instead of zip contents (CVE-2026-25645). Verified on psf/requests @ v2.32.3 (finding 15259, JOB-AD4F41).

## Strategy
- **Library-sink rule seed** — `library-sink:requests.utils.extract_zipped_paths` matched zip path extraction without race-safe validation.
- **Curated regression (bug_hunter)** — CVE-2026-25645 regression package from Iridium e2e on pinned requests revision.
- **Variant hypotheses** — Predictable-path reuse and zip-member path mutation seeds applied during harness synthesis.
- **Hunter-verify** — Isolated harness plants attacker bytes at deterministic temp path; `extract_zipped_paths` returns planted content unchanged.
- **Isolated sandbox verify** — Proof file written at `/tmp/iridium_proof` with attacker-controlled bytes preserved.
