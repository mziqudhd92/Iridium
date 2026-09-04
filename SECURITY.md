# Security Policy

## Reporting vulnerabilities

Report security issues privately to the maintainers via GitHub Security Advisories on [mziqudhd92/Iridium](https://github.com/mziqudhd92/Iridium/security/advisories/new).

Do **not** open public issues for exploitable vulnerabilities.

## Client-side threat model (Phase 1)

Iridium client tools analyze **untrusted repository contents** on the developer machine. Mitigations:

| Threat | Mitigation |
| --- | --- |
| Parser DoS | 2 MB file cap, AST depth 256, ProcessPool batches of 50, 10s batch timeout |
| Secret exfiltration via payload | Pre-AST scrubbing (PEM, JWT, API keys); string literal stripping |
| Prompt injection | Payload emits structure only (`kind`, `file`, `line`) — no raw identifiers by default |
| Cache corruption | SQLite WAL + 5s busy timeout; cross-mount fallback to `~/.cache/iridium` |

## Privacy & telemetry

| Layer | Default | Content |
| --- | --- | --- |
| Graph payload | Per scan | Structure only; `--anonymize` HMAC-hashes internal symbols |
| Product analytics | **Off** | Opt-in anonymized operational pings — zero AST/source |
| Local audit log | **Phase 1: planned** | `.iridium/audit.log` — not yet implemented |

**Opt in to analytics:** `IRIDIUM_TELEMETRY=1` or `iridium-client scan --telemetry`. We would be glad for opt-ins — they help us prioritize fixes and improve scan reliability. Pings include only coarse operational metadata (CLI version, scan duration, error classes), never repository contents.

**Always disable:** `DO_NOT_TRACK=1` or `iridium-client scan --no-telemetry`.

Graph payloads are zero-knowledge regardless of analytics setting.

## Supported versions

| Version | Supported |
| --- | --- |
| 0.6.x | ✅ Active development |
| 0.5.x | ❌ Unsupported |
| 0.1.x | ❌ Unsupported |

## API authentication

`iridium-client scan` works without an API key on the anonymous tier (rate-limited). Set `IRIDIUM_API_KEY` for authenticated tiers (higher quotas, patches, enterprise features). Never commit keys; use CI secrets.

Placeholder API host: `https://api.iridium.example.com` — configure via `IRIDIUM_API_URL`.
