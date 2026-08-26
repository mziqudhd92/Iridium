# iridium-mcp-server

MCP server for AI agent security guardrails — blocks vulnerable imports at generation time.

## Install

```bash
pip install iridium-mcp-server
```

## Cursor setup

Add to your MCP config (see `src/iridium_mcp/cursor_config.json`):

```json
{
  "mcpServers": {
    "iridium": {
      "command": "iridium-mcp-server",
      "env": {
        "IRIDIUM_API_URL": "https://api.iridium.example.com"
      }
    }
  }
}
```

No API key required for anonymous tier (rate-limited).

## Tools (Phase 2)

| Tool | Purpose |
| --- | --- |
| `validate_dependency_addition` | Check if adding a package creates reachable CVE risk |
| `get_reachability_context` | Return entrypoint → sink path + rewrite hints for agents |
| `refresh_workspace_graph` | Re-index workspace after agent saves files |

## Behavior

- **Fail-open:** API 429/5xx never blocks the agent — returns `degraded: true`
- **Background warm-index:** indexes workspace on startup before first tool call
- **Parent heartbeat:** exits cleanly when MCP parent process dies
- **Audit log:** writes to `.iridium/audit.log`

## Development

```bash
uv sync
uv run pytest packages/iridium-mcp-server/tests -v
```
