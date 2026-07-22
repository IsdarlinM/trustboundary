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

app = typer.Typer(
    name="trustboundary",
    help="Trust Boundary Mapper — explainable trust and identity-flow modeling.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
    rich_markup_mode=None,
)


def rd() -> Path:
    return Path.home() / ".trustboundary" / "workspaces"


def wp(n: str, r: Path) -> Path:
    return r / n


@app.command()
def version() -> None:
    typer.echo(__version__)


@app.command()
def doctor() -> None:
    """Check runtime, SRIC integration, plugin registry and secure defaults."""
    import sric

    plugin_path = Path.home() / ".sric" / "plugins"
    plugins = PluginRegistry(plugin_path).list()
    checks: dict[str, dict[str, object]] = {
        "python": {"ok": sys.version_info >= (3, 11), "version": sys.version.split()[0]},
        "sric": {"ok": sric.__version__.startswith("0.3."), "version": sric.__version__},
        "ai": {"ok": True, "mode": "disabled", "cloud_uploads": False},
        "plugins": {"ok": True, "count": len(plugins), "path": str(plugin_path)},
        "privacy": {"ok": True, "telemetry": False},
    }
    ok = all(bool(item["ok"]) for item in checks.values())
    typer.echo(json.dumps({"ok": ok, "checks": checks}, indent=2))
    if not ok:
        raise typer.Exit(1)


@app.command()
def init(name: str, root: Path = typer.Option(rd(), "--root")) -> None:
    root.mkdir(parents=True, exist_ok=True)
    ws = Workspace.create(root, name)
    TrustBoundaryEngine(ws.root)
    typer.echo(str(ws.root))


@app.command("workspace")
def workspace_command(
    action: str = typer.Argument("list", help="create|list|show|archive"),
    name: Optional[str] = typer.Argument(None),
    root: Path = typer.Option(rd(), "--root"),
    confirm: bool = typer.Option(False, "--confirm", help="Required for archive."),
) -> None:
    """Manage isolated investigation workspaces."""
    root.mkdir(parents=True, exist_ok=True)
    action = action.lower()
    if action == "list":
        items = sorted(p.name for p in root.iterdir() if p.is_dir() and (p / "workspace.json").is_file())
        typer.echo(json.dumps({"workspaces": items}, indent=2))
        return
    if not name:
        typer.echo(f"workspace {action} requires NAME", err=True)
        raise typer.Exit(2)
    target = wp(name, root)
    if action == "create":
        ws = Workspace.create(root, name)
        TrustBoundaryEngine(ws.root)
        typer.echo(str(ws.root))
        return
    if action == "show":
        ws = Workspace.open(target)
        meta = json.loads((ws.root / "workspace.json").read_text(encoding="utf-8"))
        typer.echo(json.dumps({"path": str(ws.root), "metadata": meta}, indent=2))
        return
    if action == "archive":
        if not confirm:
            typer.echo("workspace archive requires --confirm; no data was changed", err=True)
            raise typer.Exit(5)
        Workspace.open(target)
        archive_root = root / "archived"
        archive_root.mkdir(exist_ok=True)
        destination = archive_root / name
        if destination.exists():
            typer.echo("archive destination already exists; no data was changed", err=True)
            raise typer.Exit(2)
        target.rename(destination)
        typer.echo(str(destination))
        return
    typer.echo(f"Unknown workspace action: {action}", err=True)
    raise typer.Exit(2)


@app.command("config")
def config_command(
    action: str = typer.Argument("show", help="show|explain"),
    key: Optional[str] = typer.Argument(None),
    workspace: Optional[str] = typer.Option(None, "--workspace"),
    root: Path = typer.Option(rd(), "--root"),
) -> None:
    """Inspect configuration and explain where a value comes from."""
    defaults: dict[str, object] = {"telemetry": False, "cloud_ai": False, "external_uploads": False}
    values = dict(defaults)
    sources = {k: "secure default" for k in values}
    if workspace:
        meta_path = wp(workspace, root) / "workspace.json"
        if not meta_path.is_file():
            typer.echo("workspace.json not found", err=True)
            raise typer.Exit(2)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        for k in values:
            if k in meta:
                values[k] = meta[k]
                sources[k] = f"workspace config: {meta_path}"
    if action == "show":
        typer.echo(json.dumps({"values": values, "sources": sources}, indent=2))
        return
    if action == "explain":
        if not key or key not in values:
            typer.echo("config explain requires one of: " + ", ".join(sorted(values)), err=True)
            raise typer.Exit(2)
        typer.echo(json.dumps({"key": key, "value": values[key], "source": sources[key]}, indent=2))
        return
    typer.echo(f"Unknown config action: {action}", err=True)
    raise typer.Exit(2)


from . import cli_model as _cli_model  # noqa: E402,F401
from . import cli_analysis as _cli_analysis  # noqa: E402,F401
from . import cli_runtime as _cli_runtime  # noqa: E402,F401

@app.command("help", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def help_command(ctx: typer.Context, command: Optional[str] = typer.Argument(None)) -> None:
    if not command:
        typer.echo(ctx.parent.get_help() if ctx.parent else ctx.get_help())
        return
    root = ctx.parent.command if ctx.parent else app
    if hasattr(root, "commands") and command in root.commands:
        typer.echo(root.commands[command].get_help(ctx))
        return
    raise typer.Exit(2)


def run() -> None:
    if len(sys.argv) >= 3 and sys.argv[-1] == "help" and sys.argv[1] != "help":
        sys.argv[-1] = "--help"
    app()
