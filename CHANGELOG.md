# Changelog

All notable changes to the Iridium public OSS packages are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.5.0] - 2026-08-30

### Added

- Demo GIF and terminal cast assets in `docs/assets/`.
- `iridium_client.telemetry` module with opt-in product analytics (`--telemetry`, `IRIDIUM_TELEMETRY=1`).

### Changed

- README refreshed with NFO-style client-layer header and architecture docs.
- Product analytics are **off by default**; opt in to send anonymized operational pings.

## [0.2.0] - 2026-08-27

Phase 2 — MCP runtime guardrails and sync query API.

### Added

- **iridium-mcp-server** — stdio MCP transport with `validate_dependency_addition`, `get_reachability_context`, `refresh_workspace_graph` tools; fail-open on 429/5xx; background warm-index; parent heartbeat; `.iridium/audit.log`.
- **iridium-client** — `validate_dependency()` and `reachability_context()` query methods on `IridiumApiClient`.
- OpenAPI sync query endpoints: `POST /api/v1/client/query/validate-dependency`, `POST /api/v1/client/query/reachability-context` (MessagePack supported).

### Changed

- MCP server is production-ready for agent workflows (no longer a skeleton).

## [0.1.0] - 2026-08-27

Phase 1 initial release — client-side scanning libraries and CLI.

### Added

- **iridium-core** — `WorkspaceIndexer`, Python/JavaScript extractors, Tarjan SCC graph assembly, SQLite AST cache, lockfile parsing, pre-AST secret scrubbing, `ClientScanPayload` models.
- **iridium-client** — Typer CLI with `demo`, `scan`, and `payload dump` commands; httpx SaaS client for `/api/v1/client/scan`; Rich terminal output.
- **iridium-mcp-server** — Package skeleton with `iridium-core` dependency; stub entrypoint (Phase 2 MCP transport planned).
- OpenAPI spec (`openapi/client-scan-api-v1.yaml`) and JSON schema (`schema/client-scan-payload-v1.json`).
- CI workflow: ruff, pytest (≥80% coverage), wheel build.

### Known limitations (Phase 1)

- Local audit log (`.iridium/audit.log`) is **not implemented** — planned for a future release.
- MCP server is a skeleton — no stdio transport or tools yet.
- SaaS API host defaults to placeholder `https://api.iridium.example.com`.

[0.5.0]: https://github.com/mziqudhd92/Iridium/releases/tag/v0.5.0
[0.2.0]: https://github.com/mziqudhd92/Iridium/releases/tag/v0.2.0
[0.1.0]: https://github.com/mziqudhd92/Iridium/releases/tag/v0.1.0
