# [Vulnerability Report] UBSan division-by-zero in GGUF parser when n_heads=0

## Summary
- **Vulnerability Type:** `native.libfuzz.entrypoint`
- **Affected Location:** `c/ligguf.c:263`
- **Severity:** Low
- **Verification Status:** `confirmed_target_snippet`

**This is a zero-day vulnerability discovered by Iridium through targeted research — not an out-of-box self-learning demo path.**

## Vulnerability Details
A malformed GGUF model can leave `g_m.n_heads` at zero after tensor metadata parsing. `read_gguf` then divides by `g_m.n_heads` at `c/ligguf.c:263`, triggering UndefinedBehaviorSanitizer division-by-zero. Untrusted GGUF inputs can crash any process embedding ligguf for inference (denial of service). Verified on matrixsmaster/ligguf @ `2b5ac66` (finding 17405, JOB-9C48EC).

## Strategy
- **Targeted-research (T2R) zero-day hunt** — Iridium selected matrixsmaster/ligguf as a GGUF parser target with no prior CVE; this is a net-new finding, not a curated regression or demo path.
- **Native libFuzzer entrypoint** — `native.libfuzz.entrypoint` harness synthesized for `read_gguf` with GGUF protocol dictionary and custom mutator seeds.
- **Protocol-aware fuzzing** — Auto-generated `fuzz.dict` and `LLVMFuzzerCustomMutator` bias tensor `ne0` toward overflow edge values.
- **Witness corpus replay** — Seven witness binaries bundled; libFuzzer replay triggers UBSan at `c/ligguf.c:263` with `n_heads=0`.
- **Isolated sandbox verify** — Confirmed target snippet under UBSan in Docker (JOB-9C48EC); repo frame at cited sink line.
