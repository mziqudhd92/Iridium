# [Vulnerability Report] route-sink:chroma.update_collection

## Summary
- **Vulnerability Type:** `route-sink:chroma.update_collection`
- **Affected Location:** `chromadb/utils/embedding_functions/sentence_transformer_embedding_function.py` (`SentenceTransformerEmbeddingFunction.__init__`)
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `submission_ready`

## Vulnerability Details
`UPDATE_COLLECTION` on `/api/v2/tenants/{tenant}/databases/{database_name}/collections/{collection_id}` forwards attacker-supplied embedding configuration kwargs directly into `SentenceTransformerEmbeddingFunction(..., **kwargs)`, allowing `trust_remote_code=True` with an attacker-controlled HuggingFace repository to execute arbitrary Python code during model initialization (CVE-2026-45833, finding 15296, JOB-92C598).

## Strategy
- **Curated regression (bug_hunter)** — Route-to-sink taint traced collection update payloads into `SentenceTransformerEmbeddingFunction`.
- **Learned vuln RAG (self-learning)** — Prior model-loader `trust_remote_code` forwarding patterns prioritized kwargs pass-through sinks.
- **Deterministic harness synthesis** — Isolated `sentence_transformers.SentenceTransformer` constructor spy verified `trust_remote_code=True` reaches the underlying loader.
- **Isolated sandbox verify** — Verified under `iridium-python-verifier` with `--network none` (finding 15296, JOB-92C598).
