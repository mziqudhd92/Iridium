# [Vulnerability Report] web-route:POST:/test/connection:stdio_client

## Summary
- **Vulnerability Type:** `web-route:POST:/test/connection:stdio_client`
- **Affected Location:** `litellm/proxy/_experimental/mcp_server/rest_endpoints.py`
- **CVSS 4.0 Score:** 5.3 (MEDIUM) `CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N`
- **Verification Status:** `verified`

## Vulnerability Details
POST `/test/connection` on the MCP REST surface accepts attacker-controlled `stdio` transport with arbitrary `command` and `args`, driving subprocess execution via the MCP client test path. Verified on BerriAI/litellm @ v1.83.6-nightly (CVE-2026-42271, finding 15168, JOB-21F213).

## Strategy
- **Web route surface scan** — HTTP routes indexed; MCP REST endpoints flagged including POST `/test/connection`.
- **Route-sink rule seed** — `web-route:POST:/test/connection:stdio_client` matched stdio subprocess spawn sink in `rest_endpoints.py`.
- **Attacker reachability filter** — Test-connection handler kept as attacker-reachable on the cited revision.
- **Curated regression (bug_hunter)** — Submission-ready bounty package from Iridium e2e on BerriAI/litellm @ v1.83.6-nightly.
- **Multi-role AI pipeline** — Coder drafted FastAPI TestClient harness driving stdio command injection payload.
- **Isolated sandbox verify** — POST with `python3 -c` proof marker created `/tmp/iridium_proof` under Docker.
