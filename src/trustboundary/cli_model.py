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
def observe(workspace: str, node_id: str, name: str, node_type: NodeType, public_reachable: bool = False, root: Path = typer.Option(rd(), "--root")) -> None:
    TrustBoundaryEngine(wp(workspace, root)).add_node(Node(node_id=node_id, name=name, node_type=node_type, public_reachable=public_reachable))
    typer.echo(node_id)

@app.command("transition")
def transition_cmd(workspace: str, transition_id: str, source: str, target: str, data_type: str, input_name: Optional[str] = None, output_name: Optional[str] = None, transformation: Optional[str] = None, verified: Optional[bool] = None, evidence: list[str] = typer.Option([], "--evidence"), root: Path = typer.Option(rd(), "--root")) -> None:
    TrustBoundaryEngine(wp(workspace, root)).add_transition(Transition(transition_id=transition_id, source_node_id=source, target_node_id=target, data_type=data_type, input_name=input_name, output_name=output_name, transformation=transformation, verified=verified, evidence_ids=evidence))
    typer.echo(transition_id)

@app.command("assertion")
def assertion_cmd(workspace: str, assertion_id: str, node_id: str, statement: str, basis: str, evidence: list[str] = typer.Option([], "--evidence"), root: Path = typer.Option(rd(), "--root")) -> None:
    TrustBoundaryEngine(wp(workspace, root)).add_assertion(TrustAssertion(assertion_id=assertion_id, node_id=node_id, statement=statement, basis=basis, evidence_ids=evidence))
    typer.echo(assertion_id)

@app.command("import")
def import_cmd(workspace: str, path: Path, har: bool = typer.Option(False, "--har", help="Import HAR metadata without replaying traffic."), root: Path = typer.Option(rd(), "--root")) -> None:
    engine = TrustBoundaryEngine(wp(workspace, root))
    result = engine.import_har(path) if har or path.suffix.lower() == ".har" else engine.import_architecture(path)
    typer.echo(json.dumps(result, indent=2))

@app.command("import-config")
def import_config_cmd(workspace: str, path: Path, root: Path = typer.Option(rd(), "--root")) -> None:
    """Import supplied Kubernetes/Istio/Envoy config without contacting a cluster."""
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).import_platform_config(path), indent=2))

@app.command("assertion-dsl")
def assertion_dsl_cmd(workspace: str, path: Path, root: Path = typer.Option(rd(), "--root")) -> None:
    assertion = TrustBoundaryEngine(wp(workspace, root)).parse_assertion_dsl(path.read_text(encoding="utf-8"))
    typer.echo(assertion.model_dump_json(indent=2))

@app.command("map")
def map_cmd(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).graph(), indent=2))

@app.command()
def identities(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).identity_flows(), indent=2))

@app.command()
def assumptions(workspace: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps([x.model_dump(mode="json") for x in TrustBoundaryEngine(wp(workspace, root)).infer()], indent=2))

@app.command()
def paths(workspace: str, source: str, target: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).paths(source, target), indent=2))

@app.command()
def compare(workspace: str, node_a: str, node_b: str, root: Path = typer.Option(rd(), "--root")) -> None:
    typer.echo(json.dumps(TrustBoundaryEngine(wp(workspace, root)).compare(node_a, node_b), indent=2))

@app.command()
def validate(workspace: str, candidate_id: str, evidence: list[str] = typer.Option([], "--evidence"), confirm: bool = False, root: Path = typer.Option(rd(), "--root")) -> None:
    if not confirm or not evidence:
        typer.echo("Validation requires --confirm and evidence. No impersonation/tampering is executed automatically.", err=True)
        raise typer.Exit(5)
    e = TrustBoundaryEngine(wp(workspace, root)); d = e.store.load(); found = False
    for c in d["candidates"]:
        if c["candidate_id"] == candidate_id:
            c["status"] = "VALIDATED"; c["evidence_ids"] = sorted(set(c.get("evidence_ids", []) + evidence)); found = True
    if not found: raise typer.Exit(2)
    e.store.save(d); typer.echo(candidate_id)
