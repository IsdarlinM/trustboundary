from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from sric.plugins import PluginRegistry

from . import cli as base
from .adapters import ArchitectureProvider, normalize_architecture_export
from .core import TrustBoundaryEngine
from .layers import TrustLayerObservation, compare_trust_layers
from .models import Node, NodeType
from .provenance import IdentityProvenanceStep, analyze_identity_provenance
from .sric_bootstrap import status as sric_runtime_status

app = base.app
wp = base.wp
root_default = base.root_default


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc


def _read_list(path: Path, label: str) -> list[object]:
    raw = _read_json(path)
    if not isinstance(raw, list):
        raise typer.BadParameter(f"{label} JSON input must be a list")
    return raw


def _component_node_type(component_type: str) -> NodeType:
    lowered = component_type.casefold()
    if "gateway" in lowered:
        return NodeType.GATEWAY
    if "proxy" in lowered or "listener" in lowered:
        return NodeType.PROXY
    return NodeType.SERVICE


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
            "required": ">=0.5.13,<0.6",
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
        typer.echo(
            "\n".join(
                f"[{'OK' if item['ok'] else 'FAIL'}] {name}: {item}"
                for name, item in checks.items()
            )
        )
    if not ok:
        raise typer.Exit(1)


@app.command("import-platform")
def import_platform(
    workspace: str,
    provider: str = typer.Option(..., "--provider"),
    path: Path = typer.Option(..., "--path", exists=True, dir_okay=False),
    source_id: str = typer.Option(..., "--source-id"),
    evidence: list[str] = typer.Option([], "--evidence"),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Import a bounded architecture export as untrusted configured-state data."""
    raw = _read_json(path)
    if not isinstance(raw, dict):
        raise typer.BadParameter("architecture export JSON must be an object")
    try:
        provider_enum = ArchitectureProvider(provider.upper())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in ArchitectureProvider)
        raise typer.BadParameter(f"provider must be one of: {allowed}") from exc

    report = normalize_architecture_export(
        provider=provider_enum,
        source_id=source_id,
        data=raw,
        evidence_ids=evidence,
    )
    engine = TrustBoundaryEngine(wp(workspace, root))
    imported_nodes: list[str] = []
    for component in report.components:
        engine.add_node(
            Node(
                node_id=component.component_id,
                name=component.source_path,
                node_type=_component_node_type(component.component_type),
                metadata={
                    "provider": component.provider.value,
                    "component_type": component.component_type,
                    "listeners": component.listeners,
                    "routes": component.routes,
                    "upstreams": component.upstreams,
                    "trusted_headers": component.trusted_headers,
                    "identity_validators": component.identity_validators,
                    "source_id": source_id,
                    "configured_only": True,
                    "evidence_ids": component.evidence_ids,
                },
            )
        )
        imported_nodes.append(component.component_id)

    payload = report.model_dump(mode="json")
    payload["imported_node_ids"] = imported_nodes
    payload["runtime_edges_created"] = 0
    payload["note"] = (
        "Configured routes/upstreams are retained as metadata; runtime trust edges "
        "require explicit evidence and are not invented by the importer."
    )
    typer.echo(json.dumps(payload, indent=2, default=str))
    if report.errors:
        raise typer.Exit(2)


@app.command("layer-compare")
def layer_compare(
    intended_path: Path,
    observed_path: Path,
) -> None:
    """Compare declared/configured/observed trust samples without validating exploitability."""
    intended_raw = _read_list(intended_path, "intended/configured")
    observed_raw = _read_list(observed_path, "observed")
    observations = [
        TrustLayerObservation.model_validate(item)
        for item in [*intended_raw, *observed_raw]
    ]
    result = compare_trust_layers(observations)
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in result],
            indent=2,
            default=str,
        )
    )


@app.command("identity-trace")
def identity_trace(
    assertions_path: Path,
    edges_path: Path,
    assertion_id: str = typer.Option(
        ...,
        "--assertion-id",
        help="Identity artifact ID to trace. The option name is retained for CLI compatibility.",
    ),
    max_depth: int = typer.Option(12, "--max-depth", min=1, max=64),
) -> None:
    """Trace a bounded identity artifact through canonical provenance steps."""
    steps_raw = [
        *_read_list(assertions_path, "identity provenance"),
        *_read_list(edges_path, "identity provenance"),
    ]
    steps = [IdentityProvenanceStep.model_validate(item) for item in steps_raw]
    selected = sorted(
        (item for item in steps if item.artifact_id == assertion_id),
        key=lambda item: (item.sequence_index, item.step_id),
    )[:max_depth]
    if not selected:
        typer.echo(f"identity artifact not found: {assertion_id}", err=True)
        raise typer.Exit(2)
    reports = analyze_identity_provenance(selected)
    typer.echo(reports[0].model_dump_json(indent=2))


@app.command("identity-analyze")
def identity_analyze(assertions_path: Path, edges_path: Path) -> None:
    """Analyze canonical identity provenance; incomplete evidence remains UNKNOWN."""
    steps_raw = [
        *_read_list(assertions_path, "identity provenance"),
        *_read_list(edges_path, "identity provenance"),
    ]
    steps = [IdentityProvenanceStep.model_validate(item) for item in steps_raw]
    result = analyze_identity_provenance(steps)
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in result],
            indent=2,
            default=str,
        )
    )


@app.command("routes")
def routes_command(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """List modeled proxy/gateway trust routes from explicit transitions."""
    engine = TrustBoundaryEngine(wp(workspace, root))
    typer.echo(json.dumps(engine.proxy_chains(), indent=2, default=str))


@app.command("jwt-paths")
def jwt_paths(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """List JWT/token identity flows without assuming exploitation."""
    engine = TrustBoundaryEngine(wp(workspace, root))
    items = [
        item
        for item in engine.identity_flows()
        if str(item.get("data_type", "")).casefold() in {"jwt", "token"}
    ]
    typer.echo(json.dumps(items, indent=2, default=str))


@app.command("proxy-diff")
def proxy_diff(
    workspace: str,
    route_id: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Explain one modeled transition without claiming an exploitable proxy inconsistency."""
    engine = TrustBoundaryEngine(wp(workspace, root))
    matches = [
        item
        for item in engine.store.load()["transitions"]
        if item.get("transition_id") == route_id
    ]
    if not matches:
        typer.echo(f"route not found: {route_id}", err=True)
        raise typer.Exit(2)
    item = matches[0]
    typer.echo(
        json.dumps(
            {
                "route_id": route_id,
                "transition": item,
                "status": "OBSERVED" if item.get("evidence_ids") else "INFERRED",
                "counter_evidence": [
                    "Unmodeled intermediaries may change the effective trust path."
                ],
                "validated_exploitability": False,
            },
            indent=2,
            default=str,
        )
    )


@app.command("confusion")
def confusion_command(
    workspace: str,
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """List trust-confusion hypotheses with evidence and counter-evidence."""
    items = TrustBoundaryEngine(wp(workspace, root)).infer()
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in items],
            indent=2,
            default=str,
        )
    )


@app.command("path-search")
def path_search(
    workspace: str,
    source: str,
    target: str,
    max_depth: int = typer.Option(8, "--max-depth", min=1, max=64),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Find bounded trust paths between modeled nodes."""
    paths = TrustBoundaryEngine(wp(workspace, root)).paths(source, target)
    bounded = [path for path in paths if len(path) - 1 <= max_depth]
    typer.echo(json.dumps(bounded, indent=2, default=str))


@app.command("assumption-review")
def assumption_review(
    workspace: str,
    minimum_confidence: float = typer.Option(
        0.0,
        "--minimum-confidence",
        min=0.0,
        max=1.0,
    ),
    root: Path = typer.Option(root_default(), "--root"),
) -> None:
    """Review inferred trust assumptions conservatively."""
    items = TrustBoundaryEngine(wp(workspace, root)).infer()
    selected = [item for item in items if item.confidence >= minimum_confidence]
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in selected],
            indent=2,
            default=str,
        )
    )


def run() -> None:
    base.run()
