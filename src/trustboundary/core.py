from __future__ import annotations
from collections import defaultdict, deque
from pathlib import Path
from typing import Any
from .models import AssumptionCandidate, Node, NodeType, Transition, TrustAssertion
from .store import JsonStore
from sric.graph import GraphEdge, GraphNode, TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage, LineageRecord


MAX_IMPORT_BYTES = 10 * 1024 * 1024


def _load_json_file(path: Path) -> Any:
    if not path.is_file() or path.is_symlink():
        raise ValueError("import path must be a regular non-symlink file")
    size = path.stat().st_size
    if size > MAX_IMPORT_BYTES:
        raise ValueError(f"import exceeds {MAX_IMPORT_BYTES} byte limit")
    return __import__("json").loads(path.read_text(encoding="utf-8"))


def _upsert(items: list[dict[str, Any]], key: str, value: dict[str, Any]) -> None:
    for i, x in enumerate(items):
        if x.get(key) == value.get(key):
            items[i] = value
            return
    items.append(value)


from .core_imports import ImportMixin
from .core_analysis import AnalysisMixin

class TrustBoundaryEngine(ImportMixin, AnalysisMixin):
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.store = JsonStore(workspace)
        self.graph_store = TemporalGraph(workspace)
        self.jobs = JobEngine(workspace)
        self.lineage = EvidenceLineage(workspace)

    def add_node(self, node: Node) -> None:
        d = self.store.load()
        _upsert(d["nodes"], "node_id", node.model_dump(mode="json"))
        self.store.save(d)
        self.graph_store.upsert_node(GraphNode(node_id=f"trust:{node.node_id}", node_type=node.node_type.value, label=node.name, source="trustboundary", metadata={"public_reachable": node.public_reachable, **node.metadata}))
        self._lineage_once(LineageRecord(artifact_id=f"trust-node:{node.node_id}", artifact_type="trust_node", status="OBSERVED", source="trustboundary", method="model"))

    def add_transition(self, t: Transition) -> None:
        d = self.store.load()
        ids = {x["node_id"] for x in d["nodes"]}
        if t.source_node_id not in ids or t.target_node_id not in ids:
            raise ValueError("transition references unknown node")
        _upsert(d["transitions"], "transition_id", t.model_dump(mode="json"))
        self.store.save(d)
        self.graph_store.upsert_edge(GraphEdge(edge_id=f"trust-transition:{t.transition_id}", source_node_id=f"trust:{t.source_node_id}", target_node_id=f"trust:{t.target_node_id}", edge_type=t.data_type, observed_at=t.observed_at, evidence_ids=t.evidence_ids, discovery_method="trust_transition", metadata={"input_name": t.input_name, "output_name": t.output_name, "transformation": t.transformation, "verified": t.verified, **t.metadata}))
        self._lineage_once(LineageRecord(artifact_id=f"trust-transition:{t.transition_id}", artifact_type="trust_transition", status="OBSERVED", source="trustboundary", method="observe", evidence_ids=t.evidence_ids, parent_ids=[f"trust-node:{t.source_node_id}", f"trust-node:{t.target_node_id}"]))

    def add_assertion(self, a: TrustAssertion) -> None:
        d = self.store.load()
        _upsert(d["assertions"], "assertion_id", a.model_dump(mode="json"))
        self.store.save(d)

    def import_architecture(self, path: Path) -> dict[str, int]:
        payload = _load_json_file(path)
        n = 0
        t = 0
        a = 0
        for x in payload.get("nodes", []):
            self.add_node(Node.model_validate(x))
            n += 1
        for x in payload.get("transitions", []):
            self.add_transition(Transition.model_validate(x))
            t += 1
        for x in payload.get("assertions", []):
            self.add_assertion(TrustAssertion.model_validate(x))
            a += 1
        return {"nodes": n, "transitions": t, "assertions": a}
