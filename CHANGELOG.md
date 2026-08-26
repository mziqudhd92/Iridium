# Changelog

All notable changes to the Iridium public OSS packages are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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

[0.1.0]: https://github.com/mziqudhd92/Iridium/releases/tag/v0.1.0
