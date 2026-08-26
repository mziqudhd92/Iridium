# iridium-client

Typer CLI for Iridium reachability scanning — local AST extraction with cloud SaaS analysis.

## Install

```bash
pip install iridium-client
```

## CLI commands

### `iridium-client demo`

Run the embedded vulnerable micro-target demo (<10s, no API key, no network required for indexing).

```bash
iridium-client demo
# or zero-install:
uvx iridium-client demo
```

### `iridium-client scan`

Index a repository locally and submit the payload to Iridium SaaS. **No API key required** for the anonymous tier (rate-limited by IP).

```bash
iridium-client scan .

# Optional: override API host or authenticate for higher quotas
export IRIDIUM_API_URL=https://api.iridium.example.com
# export IRIDIUM_API_KEY=iridium_live_...
```

| Option | Description |
| --- | --- |
| `--api-url` | Override `IRIDIUM_API_URL` |
| `--anonymize` | HMAC-hash internal symbols in payload (requires `IRIDIUM_ANON_KEY`) |
| `--no-telemetry` | Disable product analytics pings |
| `--on-error pass` | Show local stats if API is unreachable (default: `block`) |

### `iridium-client payload dump`

Dump the local scan payload as JSON (zero network).

```bash
iridium-client payload dump . --validate
iridium-client payload dump . --output payload.json --validate
```

| Option | Description |
| --- | --- |
| `--validate` | Validate against `ClientScanPayload` schema |
| `--output`, `-o` | Write JSON to file instead of stdout |

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `IRIDIUM_API_URL` | `https://api.iridium.example.com` | SaaS API base URL |
| `IRIDIUM_API_KEY` | — | Optional (`X-API-Key`). Anonymous scans work without it |
| `DO_NOT_TRACK` | unset | `1` disables analytics |
| `IRIDIUM_TELEMETRY` | `1` | `0` disables analytics |
| `IRIDIUM_ANON_KEY` | — | Key for `--anonymize` mode |

Copy [`packages/iridium-client/.env.example`](.env.example) to `.env` for local development.

## Development

Part of the [Iridium monorepo](https://github.com/mziqudhd92/Iridium). From repo root:

```bash
uv sync
uv run iridium-client demo
uv run pytest packages/iridium-client/tests -v
```
