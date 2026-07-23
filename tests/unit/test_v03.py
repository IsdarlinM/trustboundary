from pathlib import Path
import json
from sric.workspace import Workspace
from trustboundary.core import TrustBoundaryEngine
from trustboundary.advanced import TrustIntelligence
from trustboundary.models import Node,NodeType,Transition

def setup_engine(tmp_path:Path):
    ws=Workspace.create(tmp_path,'w');e=TrustBoundaryEngine(ws.root);e.add_node(Node(node_id='client',name='Client',node_type=NodeType.ZONE,public_reachable=True));e.add_node(Node(node_id='gw',name='Gateway',node_type=NodeType.GATEWAY,public_reachable=True));e.add_node(Node(node_id='svc',name='Backend',node_type=NodeType.SERVICE));e.add_transition(Transition(transition_id='t1',source_node_id='client',target_node_id='gw',data_type='jwt',input_name='Authorization',output_name='X-User-ID',transformation='validated jwt sub -> header',verified=True,evidence_ids=['E1'],metadata={'validator':'gateway'}));e.add_transition(Transition(transition_id='t2',source_node_id='gw',target_node_id='svc',data_type='header',input_name='X-User-ID',output_name='X-User-ID',verified=True,evidence_ids=['E2']));return e

def test_reconstruction_and_identity_provenance(tmp_path):
    e=setup_engine(tmp_path);intel=TrustIntelligence(e);rec=intel.architecture_reconstruction_v2();assert rec['edges'][0]['status']=='OBSERVED';prov=intel.identity_provenance();assert prov[0]['validator']=='gateway' and prov[0]['validated'] is True

def test_mtls_spiffe_never_stores_private_key(tmp_path):
    e=setup_engine(tmp_path);record=TrustIntelligence(e).mtls_identity(node_id='svc',spiffe_id='spiffe://example.test/ns/default/sa/api',trust_domain='example.test',evidence_ids=['E3']);assert record['status']=='OBSERVED' and record['private_key_stored'] is False;stored=e.store.load()['mtls_identities'][0];assert set(stored).isdisjoint({'private_key_pem','private_key_value','key_material'})

def test_cloud_import_is_import_only(tmp_path):
    e=setup_engine(tmp_path);p=tmp_path/'cloud.json';p.write_text(json.dumps({'resources':[{'provider':'aws','type':'api_gateway','name':'public-api','public':True,'targets':['backend']}]}));result=TrustIntelligence(e).import_cloud_config(p);assert result['nodes']==1 and result['transitions']==1;assert any(x['metadata'].get('import_only') is True for x in e.store.load()['nodes'])

def test_assertion_library_is_conservative(tmp_path):
    e=setup_engine(tmp_path);intel=TrustIntelligence(e);ids=intel.install_assertion_library('svc');assert 'LIB-INTERNAL_SERVICE_IDENTITY_REQUIRES_MTLS' in ids;results=intel.evaluate_assertions();assert all(x['status'] in {'UNKNOWN','INFERRED','OBSERVED','HYPOTHESIS'} for x in results);assert all(x['automatic_exploitability'] is False for x in results)
