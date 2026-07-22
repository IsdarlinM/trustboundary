import json
from trustboundary.core import TrustBoundaryEngine

def test_kubernetes_ingress_import_is_declarative_only(tmp_path):
    ws = tmp_path / 'ws'
    ws.mkdir()
    (ws / 'workspace.json').write_text('{}')
    path = tmp_path / 'ingress.json'
    path.write_text(json.dumps({'apiVersion': 'networking.k8s.io/v1', 'kind': 'Ingress', 'metadata': {'name': 'public'}, 'spec': {'rules': [{'http': {'paths': [{'backend': {'service': {'name': 'api'}}}]}}]}}))
    result = TrustBoundaryEngine(ws).import_platform_config(path)
    assert result['mode'] == 'IMPORT_ONLY'
    graph = TrustBoundaryEngine(ws).graph()
    assert any((x['name'] == 'public' for x in graph['nodes']))
    assert any((x['name'] == 'api' for x in graph['nodes']))
    assert graph['transitions']

def test_trust_assertion_dsl_is_strict(tmp_path):
    ws = tmp_path / 'ws'
    ws.mkdir()
    (ws / 'workspace.json').write_text('{}')
    engine = TrustBoundaryEngine(ws)
    text = '\nASSERTION gateway_identity\nNODE gateway\nSTATEMENT X-User-ID must only exist after verified identity validation\nBASIS gateway-generated identity contract\nEVIDENCE EVD-1,EVD-2\n'
    assertion = engine.parse_assertion_dsl(text)
    assert assertion.assertion_id == 'gateway_identity'
    assert assertion.evidence_ids == ['EVD-1', 'EVD-2']
