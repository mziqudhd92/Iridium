# iridium-core

Local AST extraction, dependency graph assembly, SQLite cache, and payload models for Iridium security scanning.

**No network I/O.** No httpx dependency.

## Install

```bash
pip install iridium-core
```

## Library API

### `WorkspaceIndexer`

Primary entry point — indexes a repository into a `ClientScanPayload`:

```python
from pathlib import Path
from iridium_core import WorkspaceIndexer

indexer = WorkspaceIndexer(Path("/path/to/repo"))
payload = indexer.index()

print(payload.dependency_count, payload.entrypoint_count)
print(payload.languages)
print(payload.to_json())
```

Options:

| Parameter | Default | Description |
| --- | --- | --- |
| `use_cache` | `True` | SQLite AST cache (WAL, cross-mount fallback to `~/.cache/iridium`) |
| `use_process_pool` | `True` | ProcessPool batches for large repos (disable for small targets) |
| `extractors` | `DEFAULT_EXTRACTORS` | Custom `LanguageExtractor` plugins |

### Payload validation

```python
from iridium_core.models.payload import ClientScanPayload

validated = ClientScanPayload.model_validate(payload.model_dump())
api_dict = validated.to_api_dict()  # ready for POST /api/v1/client/scan
```

### Modules

| Module | Purpose |
| --- | --- |
| `iridium_core.extract` | Python/JavaScript `LanguageExtractor` plugins |
| `iridium_core.graph` | Tarjan SCC, bounded BFS, adjacency |
| `iridium_core.deps` | Lockfile parsing (pip, npm, etc.) |
| `iridium_core.sanitize` | Pre-AST scrubbing (PEM, JWT, API keys) |
| `iridium_core.cache` | Content-addressed AST cache |
| `iridium_core.git` | Tree hash / commit fingerprint |

## Development

Part of the [Iridium monorepo](https://github.com/mziqudhd92/Iridium). From repo root:

```bash
uv sync
uv run pytest packages/iridium-core/tests -v
```
