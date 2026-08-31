# [Vulnerability Report] route-sink:gradio.flagging_copy:/gradio_api/run/predict

## Summary
- **Vulnerability Type:** `route-sink:gradio.flagging_copy:/gradio_api/run/predict`
- **Affected Location:** `gradio/data_classes.py:0`
- **CVSS 4.0 Score:** 5.3 (MEDIUM) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
route-sink:gradio.flagging_copy:/gradio_api/run/predict

Unauthenticated POST `/gradio_api/run/predict` can drive flagging / `FileData.path` into `FileData._copy_to_dir` → `shutil.copy(self.path, dir)` with no allowlist on absolute paths (gradio>=5.25.2,<5.31.0).

## Strategy
- **Route-sink rule seed** — Static rule `route-sink:gradio.flagging_copy:/gradio_api/run/predict` matched the unauthenticated predict endpoint into the flagging copy sink.
- **Web route surface scan** — 74 HTTP routes indexed (41 unguarded); `web_route_sink_seeds` injected the flagging → `FileData._copy_to_dir` path.
- **Attacker reachability filter** — 3 attacker-reachable paths kept; 11 unreachable candidates demoted as scanner noise.
- **Attack-chain expansion (chainer)** — 5 multi-hop chains explored from API entrypoints to file-copy sinks.
- **Graph / AST enrichment** — 44 call sites marked via graphast and native reachability heuristics before ranking.
- **Context brief enrichment** — 90 findings enriched with sink context; LTR verification ranker applied.
- **Multi-role AI pipeline** — Triage → Planner → Reviewer → Reasoner → Coder drafted Python harnesses (`hunter-verify`).
- **Isolated sandbox verify** — Real `FileData._copy_to_dir` bound from target checkout; absolute-path copy proven under Docker.
