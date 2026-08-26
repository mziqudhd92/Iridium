# iridium-mcp-server

MCP server for AI agent security guardrails — **Phase 2 implementation**.

## Phase 1 status

This package is a **skeleton only** in v0.1.0:

- Package structure and `iridium-core` dependency are in place.
- `iridium-mcp-server` prints a stub message and exits.
- Planned Phase 2: stdio MCP transport, `validate_dependency` and `reachability_context` tools.

```bash
pip install iridium-mcp-server
iridium-mcp-server
# iridium-mcp-server 0.1.0 (skeleton)
```

Do not use in production agent workflows until Phase 2 ships.

## Install

```bash
pip install iridium-mcp-server
```

For local development, use the monorepo workspace:

```bash
git clone https://github.com/mziqudhd92/Iridium.git
cd Iridium
uv sync
uv run iridium-mcp-server
```

## Development

From repo root:

```bash
uv run pytest packages/iridium-mcp-server/tests -v
```

See the [monorepo README](https://github.com/mziqudhd92/Iridium#readme) for architecture and security notes.
