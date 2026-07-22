from sric.workspace import Workspace
from trustboundary.core import TrustBoundaryEngine
from trustboundary.models import Node, NodeType, Transition, TrustAssertion

def test_proxy_transformations_diff_header_contradiction_and_origin_paths(tmp_path):
    e = TrustBoundaryEngine(Workspace.create(tmp_path, 'ws').root)
    for n in [Node(node_id='internet', name='Internet', node_type=NodeType.ZONE, public_reachable=True), Node(node_id='gateway', name='Gateway', node_type=NodeType.GATEWAY), Node(node_id='backend', name='Backend', node_type=NodeType.SERVICE, public_reachable=True), Node(node_id='internal', name='Internal', node_type=NodeType.NETWORK, public_reachable=True)]:
        e.add_node(n)
    e.add_transition(Transition(transition_id='t1', source_node_id='internet', target_node_id='gateway', data_type='jwt', input_name='Authorization', output_name='X-User-ID', transformation='JWT sub -> X-User-ID', verified=True, evidence_ids=['E1'], metadata={'provenance_preserved': True}))
    e.add_transition(Transition(transition_id='t2', source_node_id='gateway', target_node_id='backend', data_type='header', input_name='X-User-ID', verified=None, evidence_ids=['E2']))
    e.add_transition(Transition(transition_id='t3', source_node_id='internal', target_node_id='backend', data_type='header', input_name='X-User-ID', verified=None, evidence_ids=['E3']))
    assert e.proxy_chains() == [['internet', 'gateway', 'backend']]
    assert len(e.identity_transformations()) == 3
    diff = e.trust_mutation_diff('internet', 'internal', 'backend')
    assert diff['status'] == 'HYPOTHESIS'
    assert e.header_provenance('X-User-ID')['confidence'] == 'HIGH'
    e.add_assertion(TrustAssertion(assertion_id='a1', node_id='backend', statement='Backend is internal only', basis='docs', evidence_ids=['E4']))
    assert e.contradictions()[0]['status'] == 'CONTRADICTED'
    assert e.direct_origin_paths()[0]['target'] == 'backend'
    assert e.jwt_metadata({'iss': 'x', 'sub': 'u', 'exp': 123, 'secret': 'no'}) == {'iss': 'x', 'sub': 'u'}
