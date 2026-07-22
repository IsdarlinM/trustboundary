from pathlib import Path
from sric.workspace import Workspace
from trustboundary.core import TrustBoundaryEngine
from trustboundary.models import Node, NodeType, Transition


def test_inference_keeps_hypothesis_and_counterevidence(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "w")
    e = TrustBoundaryEngine(ws.root)
    e.add_node(Node(node_id="g", name="Gateway", node_type=NodeType.GATEWAY, public_reachable=True))
    e.add_node(Node(node_id="b", name="Backend", node_type=NodeType.SERVICE))
    e.add_transition(Transition(transition_id="t", source_node_id="g", target_node_id="b", data_type="header", input_name="X-User-ID", verified=None, evidence_ids=["E1"]))
    c = e.infer()[0]
    assert c.status.value == "HYPOTHESIS"
    assert c.counter_evidence


def test_paths(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "w")
    e = TrustBoundaryEngine(ws.root)
    for n in ["a", "b", "c"]:
        e.add_node(Node(node_id=n, name=n, node_type=NodeType.SERVICE))
    e.add_transition(Transition(transition_id="1", source_node_id="a", target_node_id="b", data_type="data"))
    e.add_transition(Transition(transition_id="2", source_node_id="b", target_node_id="c", data_type="data"))
    assert e.paths("a", "c") == [["a", "b", "c"]]


def test_har_import_marks_client_controlled_identity_headers(tmp_path: Path) -> None:
    import json
    ws = Workspace.create(tmp_path, "har")
    engine = TrustBoundaryEngine(ws.root)
    har = tmp_path / "sample.har"
    har.write_text(json.dumps({"log":{"entries":[{"startedDateTime":"2026-01-01T00:00:00Z","request":{"url":"https://api.example.test/me","headers":[{"name":"X-User-ID","value":"123"}]}}]}}),encoding="utf-8")
    result = engine.import_har(har)
    assert result == {"hosts": 1, "transitions": 1}
    transition = engine.store.load()["transitions"][0]
    assert transition["metadata"]["client_controlled_observation"] is True
    assert engine.infer()[0].status.value == "HYPOTHESIS"
