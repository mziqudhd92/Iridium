# [Vulnerability Report] native.parser_entrypoint:gguf_init_from_file

## Summary
- **Vulnerability Type:** `native.parser_entrypoint`
- **Affected Location:** `ggml/src/gguf.cpp`
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `confirmed_target_snippet`

## Vulnerability Details
Heap-buffer-overflow in `gguf_init_from_file` when parsing malformed GGUF input. AddressSanitizer traces the write through `gguf_reader::read` at `ggml/src/gguf.cpp:285` during `gguf_init_from_file_impl` (finding 14314, JOB-3ACAB4).

## Strategy
- **Native parser entrypoint catalog** — `native.parser_entrypoint:gguf_init_from_file` ranked as a top file-format parser sink on the llama.cpp checkout.
- **LibFuzzer harness synthesis** — Auto-generated LLVMFuzzer harness feeds malformed GGUF bytes via memfd/tmp path into linked `gguf_init_from_file`.
- **Graph / AST enrichment** — Native reachability marked gguf parser call sites from model-load entrypoints.
- **Multi-candidate fan-out** — Parser entrypoints queued across ggml/gguf sources; `gguf_init_from_file` selected for isolated proof.
- **Hunter-verify** — Fuzzer witness triggered heap-buffer-overflow under AddressSanitizer in isolated Docker (tag b8145).
- **Confirmed target snippet** — Crash reproduced at `gguf.cpp:285` with deterministic fuzz corpus witness.
