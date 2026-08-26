"""Typer CLI entrypoint."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from iridium_client.api.client import IridiumApiClient
from iridium_client.demo.target import materialize_demo_target
from iridium_client.output.terminal import render_demo_graph, render_scan_results, render_zero_results
from iridium_core import WorkspaceIndexer
from iridium_core.models.payload import ClientScanPayload

app = typer.Typer(
    name="iridium-client",
    help="Iridium client — local AST extraction with cloud reachability analysis.",
    no_args_is_help=True,
)
payload_app = typer.Typer(help="Payload utilities")
app.add_typer(payload_app, name="payload")

console = Console()


@payload_app.command("dump")
def payload_dump(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, resolve_path=True),
    validate: bool = typer.Option(False, "--validate", help="Validate against schema"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write JSON to file"),
) -> None:
    """Dump local scan payload (zero network)."""
    indexer = WorkspaceIndexer(path, use_process_pool=False)
    payload = indexer.index()
    if validate:
        ClientScanPayload.model_validate(payload.model_dump())
        console.print("[green]Payload validated successfully.[/green]")
    text = payload.to_json(indent=2)
    if output:
        output.write_text(text, encoding="utf-8")
        console.print(f"Wrote payload to {output}")
    else:
        console.print(text)


@app.command()
def scan(
    path: Path = typer.Argument(Path("."), exists=True, file_okay=False, resolve_path=True),
    api_url: Optional[str] = typer.Option(None, "--api-url", envvar="IRIDIUM_API_URL"),
    anonymize: bool = typer.Option(False, "--anonymize"),
    no_telemetry: bool = typer.Option(False, "--no-telemetry"),
    on_error: str = typer.Option("block", "--on-error", help="pass|block"),
) -> None:
    """Scan a repository and submit payload to Iridium SaaS."""
    if no_telemetry or os.environ.get("DO_NOT_TRACK") == "1":
        os.environ["IRIDIUM_TELEMETRY"] = "0"

    start = time.monotonic()
    indexer = WorkspaceIndexer(path)
    payload = indexer.index()
    duration_index = time.monotonic() - start

    client = IridiumApiClient(api_url=api_url)
    try:
        response = client.submit_scan(payload.model_dump(mode="json"))
        scan_id = response.get("scan_id") or response.get("id")
        if not scan_id:
            raise RuntimeError(f"unexpected response: {response}")
        result = client.wait_for_scan(scan_id)
        render_scan_results(result, duration_s=time.monotonic() - start)
    except Exception as exc:
        if on_error == "pass":
            console.print(f"[yellow]API unreachable ({exc}); showing local stats only.[/yellow]")
            render_zero_results(
                duration_s=duration_index,
                dependency_count=payload.dependency_count,
                entrypoint_count=payload.entrypoint_count,
                languages=payload.languages,
            )
            raise typer.Exit(code=0) from exc
        console.print(f"[red]Scan failed: {exc}[/red]")
        raise typer.Exit(code=1) from exc


@app.command()
def demo() -> None:
    """Run embedded vulnerable micro-target demo (<10s)."""
    start = time.monotonic()
    target = materialize_demo_target()
    console.print(f"[dim]Demo target: {target}[/dim]")

    indexer = WorkspaceIndexer(target, use_process_pool=False)
    payload = indexer.index()

    render_demo_graph()
    console.print(
        "\n[bold]Patch preview[/bold]\n"
        "  - requests: 2.25.0 → 2.32.3\n"
        "  - pins urllib3 transitive fix for CVE-2021-33503\n"
    )

    render_zero_results(
        duration_s=time.monotonic() - start,
        dependency_count=max(payload.dependency_count, 2),
        entrypoint_count=max(payload.entrypoint_count, 1),
        languages=payload.languages or ["python"],
        reachable_count=1,
        raw_cve_count=12,
    )


if __name__ == "__main__":
    app()
