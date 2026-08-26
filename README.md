# Iridium (Public OSS)

Apache-2.0 monorepo for **client-side** security scanning: local AST extraction, graph assembly, and CLI upload to Iridium SaaS.

| Package | PyPI | Role |
| --- | --- | --- |
| `iridium-core` | `pip install iridium-core` | Extractors, cache, graph, payload models (no network) |
| `iridium-client` | `pip install iridium-client` | Typer CLI + httpx SaaS client |
| `iridium-mcp-server` | `pip install iridium-mcp-server` | MCP server for AI agents (Phase 2) |

**Private SaaS backend** (CVE intelligence, reachability workers, patches) lives in the separate `agy/iridium` repo — not here.

## Quick start

```bash
# Zero-install demo (<10s, no API key)
uvx iridium-client demo

# Local payload dump (zero network)
uvx iridium-client payload dump . --validate

# Full scan (requires IRIDIUM_API_KEY when API is live)
export IRIDIUM_API_URL=https://api.iridium.example.com
export IRIDIUM_API_KEY=iridium_live_...
iridium-client scan .
```

## Development

```bash
git clone https://github.com/mziqudhd92/Iridium.git
cd Iridium
uv sync
uv run pytest
```

### Workspace layout

```
packages/
  iridium-core/       # LanguageExtractor plugins, Tarjan SCC, AST cache
  iridium-client/     # CLI, demo, terminal output
  iridium-mcp-server/ # MCP skeleton (Phase 1)
openapi/client-scan-api-v1.yaml
schema/client-scan-payload-v1.json
```

## API contract

Stable paths under `{IRIDIUM_API_URL}/api/v1/client/*`:

- `POST /api/v1/client/scan` → 202 + `scan_id`
- `GET /api/v1/client/scan/{scan_id}` → poll findings

See [openapi/client-scan-api-v1.yaml](openapi/client-scan-api-v1.yaml) and [schema/client-scan-payload-v1.json](schema/client-scan-payload-v1.json).

## Privacy

- **Graph payloads** contain syntactic structure only — string literals and secrets are stripped client-side.
- **Product analytics** are on by default (anonymized pings); opt out with `DO_NOT_TRACK=1`, `IRIDIUM_TELEMETRY=0`, or `--no-telemetry`.
- **Local audit log** (`.iridium/audit.log`) records HTTPS metadata and is never uploaded.

See [SECURITY.md](SECURITY.md).

## License

Apache-2.0 — see [LICENSE](LICENSE). Contributions require [DCO](DCO) sign-off.
