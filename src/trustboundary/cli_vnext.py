from __future__ import annotations
import json,sys
from pathlib import Path
import typer,sric
from sric.plugins import PluginRegistry
from . import cli as base
from .advanced import TrustIntelligence
from .core import TrustBoundaryEngine
app=base.app;wp=base.wp;rd=base.rd
@app.command("doctor")
def doctor_vnext(json_output:bool=typer.Option(False,"--json"),plugin_path:Path=typer.Option(rd()/"plugins","--plugin-path"))->None:
    plugins=PluginRegistry(plugin_path).list();checks={"python":{"ok":sys.version_info>=(3,11),"version":sys.version.split()[0]},"sric":{"ok":sric.__version__.startswith("0.4."),"version":sric.__version__},"ai":{"ok":True,"mode":"disabled","cloud_uploads":False},"plugins":{"ok":True,"count":len(plugins)},"privacy":{"ok":True,"telemetry":False}};ok=all(bool(v["ok"]) for v in checks.values());typer.echo(json.dumps({"ok":ok,"checks":checks},indent=2) if json_output else "\n".join(f"[{'OK' if v['ok'] else 'FAIL'}] {k}: {v}" for k,v in checks.items()));
    if not ok:raise typer.Exit(1)
@app.command("reconstruct-v2")
def reconstruct(workspace:str,root:Path=typer.Option(rd(),"--root"))->None:typer.echo(json.dumps(TrustIntelligence(TrustBoundaryEngine(wp(workspace,root))).architecture_reconstruction_v2(),indent=2,default=str))
@app.command("identity-provenance")
def identity_provenance(workspace:str,root:Path=typer.Option(rd(),"--root"))->None:typer.echo(json.dumps(TrustIntelligence(TrustBoundaryEngine(wp(workspace,root))).identity_provenance(),indent=2,default=str))
@app.command("mtls-identity")
def mtls_identity(workspace:str,node_id:str,spiffe_id:str|None=typer.Option(None,"--spiffe-id"),san:list[str]=typer.Option([],"--san"),trust_domain:str|None=typer.Option(None,"--trust-domain"),evidence:list[str]=typer.Option([],"--evidence"),root:Path=typer.Option(rd(),"--root"))->None:
    try:payload=TrustIntelligence(TrustBoundaryEngine(wp(workspace,root))).mtls_identity(node_id=node_id,spiffe_id=spiffe_id,san=san,trust_domain=trust_domain,evidence_ids=evidence)
    except KeyError:typer.echo("Unknown node",err=True);raise typer.Exit(2)
    typer.echo(json.dumps(payload,indent=2))
@app.command("import-cloud")
def import_cloud(workspace:str,path:Path,root:Path=typer.Option(rd(),"--root"))->None:typer.echo(json.dumps(TrustIntelligence(TrustBoundaryEngine(wp(workspace,root))).import_cloud_config(path),indent=2))
@app.command("assertion-library")
def assertion_library(workspace:str,node_id:str,evaluate:bool=typer.Option(False,"--evaluate"),root:Path=typer.Option(rd(),"--root"))->None:
    intel=TrustIntelligence(TrustBoundaryEngine(wp(workspace,root)));payload={"installed":intel.install_assertion_library(node_id)}
    if evaluate:payload["results"]=intel.evaluate_assertions()
    typer.echo(json.dumps(payload,indent=2,default=str))
def run()->None:base.run()
