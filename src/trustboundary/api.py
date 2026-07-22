from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, StreamingResponse

from . import __version__
from .core import TrustBoundaryEngine
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook

HTML = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>TrustBoundary Mapper</title><style>body{font-family:system-ui;margin:0;background:#0d1117;color:#f0f6fc}header{padding:18px 24px;border-bottom:1px solid #30363d;display:flex;gap:20px}main{padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:18px}.muted{color:#8b949e}.row{padding:10px 0;border-bottom:1px solid #30363d}input{background:#0d1117;color:#fff;border:1px solid #30363d;border-radius:8px;padding:8px;width:min(420px,80vw)}</style></head><body><header><b>TrustBoundary Mapper</b><span>imr :: v__VERSION__</span><span id='jobs' class='muted'>Jobs: idle</span></header><main><input id='q' placeholder='Search architecture and assumptions'><div class='grid'><section class='card'><h3>Architecture</h3><div id='graph'></div></section><section class='card'><h3>Trust assumptions</h3><div id='assumptions'></div></section><section class='card'><h3>Identity transformations</h3><div id='transformations'></div></section><section class='card'><h3>Contradictions</h3><div id='contradictions'></div></section></div></main><script src='/assets/app.js'></script></body></html>"""
JS = """const esc=s=>String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));const row=x=>`<div class='row'>${esc(JSON.stringify(x))}</div>`;async function load(){const [g,a,t,c]=await Promise.all(['/api/graph','/api/assumptions','/api/transformations','/api/contradictions'].map(u=>fetch(u).then(r=>r.json())));graph.innerHTML=`<b>${g.nodes.length}</b> nodes · <b>${g.transitions.length}</b> transitions`+g.nodes.slice(0,20).map(row).join('');assumptions.innerHTML=a.map(row).join('')||'<span class=muted>No inferred assumptions.</span>';transformations.innerHTML=t.map(row).join('')||'<span class=muted>No identity transformations.</span>';contradictions.innerHTML=c.map(row).join('')||'<span class=muted>No modeled contradictions.</span>';document.querySelectorAll('.row').forEach(n=>n.dataset.text=n.textContent.toLowerCase())}q.oninput=()=>document.querySelectorAll('.row').forEach(n=>n.style.display=n.dataset.text.includes(q.value.toLowerCase())?'':'none');try{const es=new EventSource('/api/jobs/events');es.addEventListener('job',e=>{const j=JSON.parse(e.data);jobs.textContent='Job: '+(j.event_type||'event')})}catch(e){}load();"""


def create_app(workspace: Path) -> FastAPI:
    app = FastAPI(title="TrustBoundary Local API", version=__version__, redoc_url=None)
    engine = TrustBoundaryEngine(workspace)
    graph = TemporalGraph(workspace)
    jobs = JobEngine(workspace)
    lineage = EvidenceLineage(workspace)
    notebook = ResearchNotebook(workspace)

    @app.middleware("http")
    async def security_headers(request: Any, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.get("/", response_class=HTMLResponse)
    async def root() -> str:
        return HTML.replace("__VERSION__", __version__)

    @app.get("/assets/app.js")
    async def javascript() -> Response:
        return Response(JS, media_type="application/javascript")

    @app.get("/api/graph")
    async def architecture() -> dict[str, Any]:
        return engine.graph()

    @app.get("/api/assumptions")
    async def assumptions() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in engine.infer()]

    @app.get("/api/proxy-chains")
    async def proxy_chains() -> list[list[str]]:
        return engine.proxy_chains()

    @app.get("/api/transformations")
    async def transformations() -> list[dict[str, Any]]:
        return engine.identity_transformations()

    @app.get("/api/contradictions")
    async def contradictions() -> list[dict[str, Any]]:
        return engine.contradictions()

    @app.get("/api/origin-paths")
    async def origin_paths() -> list[dict[str, Any]]:
        return engine.direct_origin_paths()

    @app.get("/api/search")
    async def search(q: str, limit: int = 50) -> list[dict[str, Any]]:
        return graph.search(q, max(1, min(limit, 500)))

    @app.get("/api/jobs")
    async def list_jobs() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in jobs.list()]

    @app.get("/api/jobs/events")
    async def job_events(cursor: int = 0, once: bool = False) -> StreamingResponse:
        async def stream() -> Any:
            current = max(0, cursor)
            while True:
                events = jobs.all_events(current)
                for event in events:
                    yield f"id: {current}\nevent: job\ndata: {json.dumps(event.model_dump(mode='json'), default=str)}\n\n"
                    current += 1
                if once:
                    if not events:
                        yield "event: heartbeat\ndata: {}\n\n"
                    break
                await asyncio.sleep(1)
        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"})

    @app.get("/api/notebook")
    async def notebook_entries() -> list[dict[str, Any]]:
        return [x.model_dump(mode="json") for x in notebook.list()]

    @app.get("/api/evidence-lineage/{artifact_id:path}")
    async def evidence_lineage(artifact_id: str) -> dict[str, Any]:
        try:
            return lineage.explain(artifact_id)
        except KeyError:
            return {"artifact_id": artifact_id, "status": "UNKNOWN", "message": "No lineage record found."}

    return app
