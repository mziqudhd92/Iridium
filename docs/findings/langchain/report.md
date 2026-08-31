# [Vulnerability Report] ai.prompt.load_prompt

## Summary
- **Vulnerability Type:** `ai.prompt.load_prompt`
- **Affected Location:** `libs/core/langchain_core/prompts/loading.py:56`
- **CVSS 4.0 Score:** 9.3 (CRITICAL) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
Rule: ai.prompt.load_prompt
Severity: HIGH
Summary: _load_template() reads config-provided paths without an obvious resolve/commonpath guard.
Location: libs/core/langchain_core/prompts/loading.py:56
Function: _load_template()
Hit line: template = template_path.read_text(encoding="utf-8")
Why it matters: Configuration-driven prompt and model loaders often treat attacker-controlled fields such as template_path or examples as local file paths or fetch targets. Without canonicalization and boundary checks, they can expose arbitrary files.
Hunter next step: Check for Path.resolve or os.path.realpath followed by os.path.commonpath before open/read/fetch.
Snippet:
template = template_path.read_text(encoding="utf-8")

## Strategy
- **Targeted-research rule** — `ai.prompt.load_prompt` flagged `_load_template()` reading attacker-controlled `template_path` without boundary checks.
- **Offensive memory (self-learning)** — 12 prior prompt-loader patterns recalled from verified hunts and boosted this sink in the candidate pool.
- **Schema + fixture seeds** — 13 pydantic/fixture payloads generated to probe config-driven template loaders.
- **Variant hypotheses** — Path-traversal mutation seeds applied (e.g. `....//....//etc/hosts`) during harness synthesis.
- **Tool-hijack seeds** — 12 agent-tool surfaces scanned for config path injection into prompt loaders.
- **Repo-class priors** — Library classification (`python=2451` modules) tuned top-N verification budget for loader sinks.
- **Multi-role AI pipeline** — Reasoner confirmed missing `resolve`/`commonpath`; Coder drafted isolated `_load_template` harness.
- **Reasoner reachability filter** — 26 low-confidence hypotheses demoted; top brief pool kept for verification.
- **Isolated sandbox verify** — Config `template_path` read a local secret file; no traversal guards on cited function.
