"""Terminal output reporter."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

console = Console()


def _is_reachable_finding(finding: dict[str, Any]) -> bool:
    if finding.get("sca_reachable") is True:
        return True
    if finding.get("sca_reachability") == "reachable":
        return True
    return finding.get("reachable") is True


def _scan_summary_fields(result: dict[str, Any]) -> dict[str, Any]:
    summary = result.get("summary")
    if not isinstance(summary, dict):
        summary = {}
    return {
        "dependency_count": summary.get("dependency_count", result.get("dependency_count", 0)),
        "entrypoint_count": summary.get("entrypoint_count", result.get("entrypoint_count", 0)),
        "languages": summary.get("languages", result.get("languages", [])),
        "reachable_count": summary.get(
            "reachable_finding_count",
            result.get("reachable_finding_count", result.get("reachable_count", 0)),
        ),
        "raw_cve_count": summary.get("raw_cve_count", result.get("raw_cve_count")),
        "cve_database_count": summary.get(
            "cve_database_count", result.get("cve_database_count", 847)
        ),
    }


def render_zero_results(
    *,
    duration_s: float,
    dependency_count: int,
    entrypoint_count: int,
    languages: list[str],
    cve_database_count: int = 847,
    reachable_count: int = 0,
    raw_cve_count: int | None = None,
) -> None:
    """Explicit negative state when no reachable vulnerabilities found."""
    suppressed = 0
    if raw_cve_count is not None and raw_cve_count > reachable_count:
        suppressed = int(((raw_cve_count - reachable_count) / raw_cve_count) * 100)

    lang_str = ", ".join(languages) if languages else "none"
    lines = [
        f"✓ Scan complete ({duration_s:.1f}s)",
        (
            f"  {dependency_count} dependencies analyzed · "
            f"{entrypoint_count} API entrypoints · {lang_str}"
        ),
        f"  {cve_database_count} CVEs in database · {reachable_count} reachable paths detected",
    ]
    if suppressed:
        lines.append(
            f"  Iridium suppressed {suppressed}% of raw CVE noise "
            f"({raw_cve_count - reachable_count} unreachable)"
        )
    lines.append("")
    lines.append("  No action required. Run `iridium-client demo` to see reachability in action.")
    console.print(Panel("\n".join(lines), title="Iridium", border_style="green"))


def render_scan_results(result: dict[str, Any], *, duration_s: float) -> None:
    """Render scan poll response."""
    findings = result.get("findings") or []
    reachable = [f for f in findings if _is_reachable_finding(f)]
    summary = _scan_summary_fields(result)
    if not reachable:
        render_zero_results(
            duration_s=duration_s,
            dependency_count=int(summary["dependency_count"]),
            entrypoint_count=int(summary["entrypoint_count"]),
            languages=list(summary["languages"]),
            reachable_count=int(summary["reachable_count"]),
            raw_cve_count=summary["raw_cve_count"],
            cve_database_count=int(summary["cve_database_count"]),
        )
        return

    tree = Tree(f"[bold]Reachable findings ({len(reachable)})[/bold]")
    for finding in reachable[:20]:
        cve = finding.get("cve_id") or finding.get("rule_id", "unknown")
        path = finding.get("path") or finding.get("package", "")
        tree.add(f"{cve}: {path}")
    console.print(Panel(tree, title=f"Scan complete ({duration_s:.1f}s)", border_style="yellow"))


def render_demo_graph() -> None:
    """ASCII reachability graph for demo command."""
    graph = """
  [HTTP] GET /fetch
    └─► handler()
          └─► requests.get(url)
                └─► [CVE sink] CVE-2021-33503 (requests < 2.26)
"""
    console.print(Panel(graph.strip(), title="Reachability graph (demo)", border_style="cyan"))
