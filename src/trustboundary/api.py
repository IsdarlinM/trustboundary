from __future__ import annotations
import asyncio,json
from pathlib import Path
from typing import Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse,HTMLResponse,Response
from . import __version__
from sric.graph import TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage
from sric.notebook import ResearchNotebook
from .core import TrustBoundaryEngine
from .advanced import TrustIntelligence
HTML="""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>TrustBoundary Mapper</title></head><body><header><b>TrustBoundary Mapper</b><span>imr :: v__VERSION__</span></header><main><div id='graph'></div></main><script src='/assets/app.js'></script></body></html>"""
JS="""async function load(){const g=await fetch('/api/graph').then(r=>r.json());document.getElementById('graph').textContent=JSON.stringify(g,null,2)}load()"""
def create_app(workspace:Path)->FastAPI:
    app=FastAPI(title='TrustBoundary Local API',version=__version__,redoc_url=None);engine=TrustBoundaryEngine(workspace);graph=TemporalGraph(workspace);jobs=JobEngine(workspace);lineage=EvidenceLineage(workspace);notebook=ResearchNotebook(workspace)
    @app.middleware('http')
    async def hdr(req:Any,call_next:Any)->Any:
        response=await call_next(req);response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'";response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='no-referrer';return response
    @app.get('/',response_class=HTMLResponse)
    async def root()->str:return HTML.replace('__VERSION__',__version__)
    @app.get('/assets/app.js')
    async def js()->Response:return Response(JS,media_type='application/javascript')
    @app.get('/api/graph')
    async def api_graph()->dict[str,Any]:return engine.graph()
    @app.get('/api/assumptions')
    async def assumptions()->list[dict[str,Any]]:return [x.model_dump(mode='json') for x in engine.infer()]
    @app.get('/api/proxy-chains')
    async def proxy_chains()->list[list[str]]:return engine.proxy_chains()
    @app.get('/api/transformations')
    async def transformations()->list[dict[str,Any]]:return engine.identity_transformations()
    @app.get('/api/contradictions')
    async def contradictions()->list[dict[str,Any]]:return engine.contradictions()
    @app.get('/api/origin-paths')
    async def origin_paths()->list[dict[str,Any]]:return engine.direct_origin_paths()
    @app.get('/api/reconstruction-v2')
    async def reconstruction_v2()->dict[str,Any]:return TrustIntelligence(engine).architecture_reconstruction_v2()
    @app.get('/api/identity-provenance')
    async def identity_provenance()->list[dict[str,Any]]:return TrustIntelligence(engine).identity_provenance()
    @app.get('/api/assertion-results')
    async def assertion_results()->list[dict[str,Any]]:return TrustIntelligence(engine).evaluate_assertions()
    @app.get('/api/search')
    async def search(q:str,limit:int=50)->list[dict[str,Any]]:return graph.search(q,max(1,min(limit,500)))
    @app.get('/api/jobs')
    async def list_jobs()->list[dict[str,Any]]:return [x.model_dump(mode='json') for x in jobs.list()]
    @app.get('/api/jobs/events')
    async def job_events(cursor:int=0,once:bool=False)->StreamingResponse:
        async def stream()->Any:
            current=max(0,cursor)
            while True:
                events=jobs.all_events(current)
                for event in events:
                    yield f"id: {current}\nevent: job\ndata: {json.dumps(event.model_dump(mode='json'),default=str)}\n\n";current+=1
                if once:
                    if not events:yield 'event: heartbeat\ndata: {}\n\n'
                    break
                await asyncio.sleep(1)
        return StreamingResponse(stream(),media_type='text/event-stream')
    @app.get('/api/notebook')
    async def notes()->list[dict[str,Any]]:return [x.model_dump(mode='json') for x in notebook.list()]
    @app.get('/api/evidence-lineage/{artifact_id:path}')
    async def explain(artifact_id:str)->dict[str,Any]:
        try:return lineage.explain(artifact_id)
        except KeyError:return {'artifact_id':artifact_id,'status':'UNKNOWN','message':'No lineage record found.'}
    return app
