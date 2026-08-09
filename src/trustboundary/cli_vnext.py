from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from sric.plugins import PluginRegistry

from . import cli as base
from .adapters import ArchitectureProvider, normalize_architecture_export
from .advanced import TrustIntelligence
from .core import TrustBoundaryEngine
from .layers import TrustLayerObservation, analyze_forwarding_headers, compare_trust_layers
from .provenance import IdentityProvenanceStep, analyze_identity_provenance
from .sric_bootstrap import status as sric_runtime_status

app = base.app
wp = base.wp
rd = base.rd


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


@app.command("doctor")
def doctor_vnext(
    json_output: bool = typer.Option(False, "--json"),
    plugin_path: Path = typer.Option(rd() / "plugins", "--plugin-path"),
) -> None:
    """Check Python, exact SRIC feature compatibility, plugins and privacy."""
    plugins = PluginRegistry(plugin_path).list()
    runtime = sric_runtime_status()
    checks = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {"ok": runtime.compatible, "version": runtime.version, "required": ">=0.5.7,<0.6", "missing_modules": list(runtime.missing_modules), "reasons": list(runtime.reasons)},
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(value["ok"]) for value in checks.values())
    if json_output:
        typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    else:
        typer.echo("\n".join(f"[{'OK' if value['ok'] else 'FAIL'}] {name}: {value}" for name, value in checks.items()))
    if not ok:
        raise typer.Exit(1)


@app.command("reconstruct-v2")
def reconstruct(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    """Reconstruct evidence-bearing trust paths conservatively."""
    engine = TrustBoundaryEngine(wp(workspace, root))
    output = TrustIntelligence(engine).architecture_reconstruction_v2()
    typer.echo(json.dumps(output, indent=2, default=str))


@app.command("identity-provenance")
def identity_provenance(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    """Show identity origin, validator, transformation and consumer evidence."""
    engine = TrustBoundaryEngine(wp(workspace, root))
    output = TrustIntelligence(engine).identity_provenance()
    typer.echo(json.dumps(output, indent=2, default=str))


@app.command("mtls-identity")
def mtls_identity(
    workspace: str,
    node_id: str,
    spiffe_id: str | None = typer.Option(None, "--spiffe-id"),
    san: list[str] = typer.Option([], "--san"),
    trust_domain: str | None = typer.Option(None, "--trust-domain"),
    evidence: list[str] = typer.Option([], "--evidence"),
    root: Path = typer.Option(rd(), "--root"),
) -> None:
    """Attach mTLS/SPIFFE metadata without storing private keys."""
    try:
        payload = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root))).mtls_identity(node_id=node_id, spiffe_id=spiffe_id, san=san, trust_domain=trust_domain, evidence_ids=evidence)
    except KeyError as exc:
        typer.echo("Unknown node", err=True)
        raise typer.Exit(2) from exc
    typer.echo(json.dumps(payload, indent=2))


@app.command("import-cloud")
def import_cloud(workspace: str, path: Path, root: Path = typer.Option(rd(), "--root")) -> None:
    """Import a local cloud configuration as untrusted data only."""
    engine = TrustBoundaryEngine(wp(workspace, root))
    payload = TrustIntelligence(engine).import_cloud_config(path)
    typer.echo(json.dumps(payload, indent=2))


@app.command("assertion-library")
def assertion_library(workspace: str, node_id: str, evaluate: bool = typer.Option(False, "--evaluate"), root: Path = typer.Option(rd(), "--root")) -> None:
    """Install or evaluate conservative trust assertions."""
    intelligence = TrustIntelligence(TrustBoundaryEngine(wp(workspace, root)))
    payload: dict[str, object] = {"installed": intelligence.install_assertion_library(node_id)}
    if evaluate:
        payload["results"] = intelligence.evaluate_assertions()
    typer.echo(json.dumps(payload, indent=2, default=str))


@app.command("layer-compare")
def layer_compare(path: Path) -> None:
    """Compare declared, configured and observed trust paths from JSON."""
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("trust-layer observations JSON must be a list")
    observations = [TrustLayerObservation.model_validate(item) for item in raw]
    output = compare_trust_layers(observations)
    typer.echo(json.dumps([item.model_dump(mode="json") for item in output], indent=2, default=str))


@app.command("headers-analyze")
def headers_analyze(path: Path) -> None:
    """Analyze forwarding-header duplicates and ambiguity without trusting them."""
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("headers JSON must be a list of [name, value] pairs")
    pairs: list[tuple[str, str]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, list) or len(item) != 2:
            raise typer.BadParameter(f"headers[{index}] must contain name and value")
        pairs.append((str(item[0]), str(item[1])))
    typer.echo(analyze_forwarding_headers(pairs).model_dump_json(indent=2))


@app.command("architecture-import")
def architecture_import(
    path: Path,
    provider: ArchitectureProvider = typer.Option(..., "--provider", case_sensitive=False),
    source_id: str = typer.Option(..., "--source-id"),
    evidence: list[str] = typer.Option([], "--evidence"),
) -> None:
    """Validate a provider export as declared/configured architecture only."""
    raw = _read_json(path)
    if not isinstance(raw, dict):
        raise typer.BadParameter("architecture export JSON must be an object")
    report = normalize_architecture_export(provider=provider, source_id=source_id, data=raw, evidence_ids=evidence)
    typer.echo(report.model_dump_json(indent=2))
    if report.errors:
        raise typer.Exit(2)


@app.command("provenance-analyze")
def provenance_analyze(path: Path) -> None:
    """Analyze token exchange and signed-header provenance from JSON records."""
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter("provenance steps JSON must be a list")
    steps = [IdentityProvenanceStep.model_validate(item) for item in raw]
    output = analyze_identity_provenance(steps)
    typer.echo(json.dumps([item.model_dump(mode="json") for item in output], indent=2, default=str))
    if any(item.status.value == "UNKNOWN" for item in output):
        raise typer.Exit(2)


def run() -> None:
    base.run()
