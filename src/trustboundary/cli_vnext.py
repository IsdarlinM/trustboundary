from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from sric.plugins import PluginRegistry
from sric.models import Confidence

from . import cli as base
from .adapters import import_architecture
from .advanced import TrustIntelligence
from .core import TrustBoundaryEngine
from .layers import IntendedTrustRule, ObservedTrustEvent, compare_trust_layers
from .provenance import IdentityAssertion, ProvenanceEdge, analyze_identity_provenance, trace_identity_provenance
from .sric_bootstrap import status as sric_runtime_status

app = base.app
wp = base.wp
root_default = base.root_default


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


@app.command("doctor")
def doctor_vnext(
    json_output: bool = typer.Option(False, "--json"),
    plugin_path: Path = typer.Option(root_default() / "plugins", "--plugin-path"),
) -> None:
    """Check Python, exact SRIC feature compatibility, plugins and privacy."""
    plugins = PluginRegistry(plugin_path).list()
    runtime = sric_runtime_status()
    checks = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {
            "ok": runtime.compatible,
            "version": runtime.version,
            "required": ">=0.5.12,<0.6",
            "missing_modules": list(runtime.missing_modules),
            "reasons": list(runtime.reasons),
        },
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(item["ok"]) for item in checks.values())
    if json_output:
        typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    else:
        typer.echo("\n".join(f"[{'OK' if item['ok'] else 'FAIL'}] {name}: {item}" for name, item in checks.items()))
    if not ok:
        raise typer.Exit(1)


@app.command("import-platform")
def import_platform(
    workspace: str,
    provider: str = typer.Option(..., "--provider"),
    path: Path = typer.Option(..., "--path"),
    source_id: str = typer.Option(..., "--source-id"),
    evidence: list[str] = typer.Option([], "--evidence"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Import a bounded architecture export as untrusted data with explicit provenance."""
    raw = _read_json(path)
    if not isinstance(raw, dict):
        raise typer.BadParameter("architecture export JSON must be an object")
    report = import_architecture(provider=provider, source_id=source_id, data=raw, evidence_ids=evidence)
    engine = TrustBoundaryEngine(wp(workspace, root))
    for asset in report.assets:
        engine.add_asset(asset)
    for edge in report.edges:
        engine.add_edge(edge)
    for assumption in report.assumptions:
        engine.add_assumption(assumption)
    typer.echo(report.model_dump_json(indent=2))
    if report.errors:
        raise typer.Exit(2)


@app.command("layer-compare")
def layer_compare(
    intended_path: Path,
    observed_path: Path,
) -> None:
    """Compare intended/configured and observed trust behavior without validating findings."""
    intended_raw = _read_json(intended_path)
    observed_raw = _read_json(observed_path)
    if not isinstance(intended_raw, list) or not isinstance(observed_raw, list):
        raise typer.BadParameter("intended and observed JSON inputs must both be lists")
    intended = [IntendedTrustRule.model_validate(item) for item in intended_raw]
    observed = [ObservedTrustEvent.model_validate(item) for item in observed_raw]
    result = compare_trust_layers(intended, observed)
    typer.echo(json.dumps([item.model_dump(mode="json") for item in result], indent=2, default=str))


@app.command("identity-trace")
def identity_trace(
    assertions_path: Path,
    edges_path: Path,
    assertion_id: str = typer.Option(..., "--assertion-id"),
    max_depth: int = typer.Option(12, "--max-depth", min=1, max=64),
) -> None:
    """Trace identity provenance through bounded evidence-bearing edges."""
    assertions_raw = _read_json(assertions_path)
    edges_raw = _read_json(edges_path)
    if not isinstance(assertions_raw, list) or not isinstance(edges_raw, list):
        raise typer.BadParameter("assertions and edges JSON inputs must both be lists")
    assertions = [IdentityAssertion.model_validate(item) for item in assertions_raw]
    edges = [ProvenanceEdge.model_validate(item) for item in edges_raw]
    result = trace_identity_provenance(assertions, edges, assertion_id, max_depth=max_depth)
    typer.echo(result.model_dump_json(indent=2))


@app.command("identity-analyze")
def identity_analyze(assertions_path: Path, edges_path: Path) -> None:
    """Analyze identity provenance conservatively; absence of evidence remains UNKNOWN."""
    assertions_raw = _read_json(assertions_path)
    edges_raw = _read_json(edges_path)
    if not isinstance(assertions_raw, list) or not isinstance(edges_raw, list):
        raise typer.BadParameter("assertions and edges JSON inputs must both be lists")
    assertions = [IdentityAssertion.model_validate(item) for item in assertions_raw]
    edges = [ProvenanceEdge.model_validate(item) for item in edges_raw]
    result = analyze_identity_provenance(assertions, edges)
    typer.echo(json.dumps([item.model_dump(mode="json") for item in result], indent=2, default=str))


@app.command("routes")
def routes_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """List modeled trust routes and evidence-aware summaries."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    typer.echo(json.dumps(intelligence.routes(), indent=2, default=str))


@app.command("jwt-paths")
def jwt_paths(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """List JWT/token trust paths without assuming exploitation."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    typer.echo(json.dumps(intelligence.jwt_paths(), indent=2, default=str))


@app.command("proxy-diff")
def proxy_diff(
    workspace: str,
    route_id: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Compare proxy/gateway transformations for a modeled route."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    try:
        result = intelligence.proxy_diff(route_id)
    except KeyError as exc:
        typer.echo(f"route not found: {route_id}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(result, indent=2, default=str))


@app.command("confusion")
def confusion_command(workspace: str, root: Path = typer.Option(root_default(), "--root")) -> None:
    """List trust-confusion hypotheses with evidence/counter-evidence/confidence."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    typer.echo(json.dumps([item.model_dump(mode="json") for item in intelligence.confusion_hypotheses()], indent=2, default=str))


@app.command("path-search")
def path_search(
    workspace: str,
    source: str,
    target: str,
    max_depth: int = typer.Option(8, "--max-depth", min=1, max=64),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Find bounded trust paths between modeled nodes."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    typer.echo(json.dumps(intelligence.path_search(source, target, max_depth=max_depth), indent=2, default=str))


@app.command("assumption-review")
def assumption_review(
    workspace: str,
    minimum_confidence: float = typer.Option(0.0, "--minimum-confidence", min=0.0, max=1.0),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Review trust assumptions with explainable confidence and evidence."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    results = intelligence.assumption_review(Confidence(value=minimum_confidence))
    typer.echo(json.dumps([item.model_dump(mode="json") for item in results], indent=2, default=str))


def run() -> None:
    base.run()
