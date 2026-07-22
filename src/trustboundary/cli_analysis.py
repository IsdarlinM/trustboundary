# ruff: noqa: F401
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional
import typer
from sric.workspace import Workspace
from sric.evidence import EvidenceStore
from sric.models import Provenance, ProvenanceType
from sric.plugins import PluginRegistry
from sric.scope import ScopeEngine, ScopePolicy
from sric.updater import perform_update
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import NotebookEntry, ResearchNotebook
from . import __version__
from .api import create_app
from .core import TrustBoundaryEngine
from .models import Node, NodeType, Transition, TrustAssertion
from .cli import app, rd, wp

@app.command()
def timeline(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    data = TrustBoundaryEngine(wp(workspace, root)).store.load()
    events = [{"time": x.get("observed_at"), "type": "transition", "id": x.get("transition_id")} for x in data["transitions"]]
    typer.echo(json.dumps(sorted(events, key=lambda x: x["time"] or ""), indent=2))

@app.command("proxy-chains")
def proxy_chains_command(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).proxy_chains(), indent=2))

@app.command("transformations")
def transformations_command(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).identity_transformations(), indent=2))

@app.command("trust-diff")
def trust_diff_command(workspace: str, source_a: str, source_b: str, target: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).trust_mutation_diff(source_a, source_b, target), indent=2))

@app.command("jwt")
def jwt_command(workspace: str, file: Path = typer.Argument(..., exists=True, dir_okay=False), root: Path = typer.Option(rd(), "--root")) -> None:
    claims=json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(claims, dict):
        typer.echo("JWT claims input must be a JSON object", err=True); raise typer.Exit(2)
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).jwt_metadata(claims), indent=2))

@app.command("header-provenance")
def header_provenance_command(workspace: str, header: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).header_provenance(header), indent=2))

@app.command("contradictions")
def contradictions_command(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).contradictions(), indent=2))

@app.command("origin-paths")
def origin_paths_command(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).direct_origin_paths(), indent=2))

@app.command("export")
def export_cmd(workspace: str, output: Path, root: Path = typer.Option(rd(), "--root")) -> None:
    output.write_text(json.dumps(TrustBoundaryEngine(wp(workspace, root)).graph(), indent=2), encoding="utf-8"); typer.echo(str(output))

@app.command()
def report(workspace: str, output: Path, root: Path = typer.Option(rd(), "--root")) -> None:
    e = TrustBoundaryEngine(wp(workspace, root)); c = e.infer()
    output.write_text("# TrustBoundary Report\n\n## Facts\n```json\n" + json.dumps(e.graph(), indent=2) + "\n```\n\n## Inferred assumptions\n```json\n" + json.dumps([x.model_dump(mode="json") for x in c], indent=2) + "\n```\n\nInference does not establish exploitability.\n", encoding="utf-8")
    typer.echo(str(output))

@app.command()
def demo(workspace: str = "demo", root: Path = typer.Option(rd(), "--root")) -> None:
    path = wp(workspace, root)
    if not path.exists(): root.mkdir(parents=True, exist_ok=True); Workspace.create(root, workspace)
    e = TrustBoundaryEngine(path)
    e.add_node(Node(node_id="internet", name="Internet", node_type=NodeType.ZONE, public_reachable=True)); e.add_node(Node(node_id="gw", name="API Gateway", node_type=NodeType.GATEWAY, public_reachable=True)); e.add_node(Node(node_id="backend", name="Backend", node_type=NodeType.SERVICE))
    e.add_transition(Transition(transition_id="t1", source_node_id="internet", target_node_id="gw", data_type="identity", input_name="JWT", output_name="X-User-ID", transformation="JWT sub -> X-User-ID", verified=True, evidence_ids=["E1"])); e.add_transition(Transition(transition_id="t2", source_node_id="gw", target_node_id="backend", data_type="header", input_name="X-User-ID", verified=None, evidence_ids=["E2"]))
    typer.echo(json.dumps([x.model_dump(mode="json") for x in e.infer()], indent=2))
