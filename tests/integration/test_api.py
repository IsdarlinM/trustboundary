from pathlib import Path
from fastapi.testclient import TestClient
from sric.workspace import Workspace
from trustboundary.api import create_app

def test_api(tmp_path:Path)->None:
    ws=Workspace.create(tmp_path,'w');c=TestClient(create_app(ws.root));r=c.get('/');assert r.status_code==200 and "script-src 'self'" in r.headers['content-security-policy'];assert c.get('/assets/app.js').status_code==200;assert c.get('/api/graph').json()['nodes']==[]

def test_v03_api_surfaces(tmp_path:Path)->None:
    ws=Workspace.create(tmp_path,'v03');c=TestClient(create_app(ws.root));rec=c.get('/api/reconstruction-v2');assert rec.status_code==200 and rec.json()['principle'].endswith('exploitability.');assert c.get('/api/identity-provenance').json()==[];assert c.get('/api/assertion-results').json()==[]
