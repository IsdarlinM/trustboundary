from __future__ import annotations
# ruff: noqa: F401
from collections import defaultdict, deque
from pathlib import Path
from typing import Any
from .models import AssumptionCandidate, Node, NodeType, Transition, TrustAssertion
from .store import JsonStore
from sric.graph import GraphEdge, GraphNode, TemporalGraph
from sric.jobs import JobEngine
from sric.lineage import EvidenceLineage, LineageRecord

MAX_IMPORT_BYTES = 10 * 1024 * 1024

class AnalysisMixin:
    def graph(self) -> dict[str, Any]:
        return self.store.load()

    def identity_flows(self) -> list[dict[str, Any]]:
        d = self.store.load()
        return [x for x in d["transitions"] if x["data_type"].lower() in {"identity", "header", "jwt", "token", "credential"}]

    def paths(self, source: str, target: str) -> list[list[str]]:
        d = self.store.load()
        adj: dict[str, list[str]] = defaultdict(list)
        for x in d["transitions"]:
            adj[x["source_node_id"]].append(x["target_node_id"])
        out = []
        q = deque([(source, [source])])
        while q:
            cur, path = q.popleft()
            if len(path) > 12:
                continue
            for nxt in adj[cur]:
                if nxt in path:
                    continue
                np = path + [nxt]
                if nxt == target:
                    out.append(np)
                else:
                    q.append((nxt, np))
        return out

    def infer(self) -> list[AssumptionCandidate]:
        d = self.store.load()
        nodes = {x["node_id"]: Node.model_validate(x) for x in d["nodes"]}
        out: list[AssumptionCandidate] = []
        for raw in d["transitions"]:
            t = Transition.model_validate(raw)
            src = nodes[t.source_node_id]
            dst = nodes[t.target_node_id]
            name = (t.output_name or t.input_name or "").lower()
            evidence = t.evidence_ids
            counter = []
            reason = []
            confidence = 0.5
            title = None
            if t.data_type.lower() in {"identity", "header", "jwt", "token"} and t.verified is not True:
                if name.startswith("x-") or "user" in name or "identity" in name or "jwt" in t.data_type.lower():
                    title = f"Potential unverified identity trust transition: {src.name} → {dst.name}"
                    reason.append("Identity-bearing data crosses a service boundary without observed verification evidence.")
                    confidence = 0.72
                    if t.transformation:
                        reason.append(f"Observed transformation: {t.transformation}.")
                        confidence += 0.05
                    counter.append("Verification may occur in code or infrastructure not represented in the imported evidence.")
            if src.public_reachable and dst.node_type in {NodeType.SERVICE, NodeType.GATEWAY} and (t.metadata.get("trust_basis") == "network_location"):
                title = f"Potential network-location trust assumption at {dst.name}"
                reason.append("A publicly reachable path is associated with a network-location trust basis.")
                confidence = max(confidence, 0.78)
                counter.append("Network controls outside the observed architecture may restrict the effective path.")
            if title:
                out.append(AssumptionCandidate(candidate_id=f"TBC-{len(out) + 1:04d}", title=title, confidence=min(confidence, 0.95), node_ids=[src.node_id, dst.node_id], evidence_ids=evidence, counter_evidence=counter, reasoning=reason, limitations=["Inference does not establish exploitability.", "Active impersonation or header tampering is not performed automatically."]))
        d["candidates"] = [x.model_dump(mode="json") for x in out]
        self.store.save(d)
        return out

    def _lineage_once(self, record: LineageRecord) -> None:
        try:
            self.lineage.explain(record.artifact_id)
        except KeyError:
            self.lineage.append(record)

    def proxy_chains(self) -> list[list[str]]:
        """Reconstruct candidate proxy/gateway chains only from modeled transitions."""
        d = self.store.load()
        nodes = {x["node_id"]: Node.model_validate(x) for x in d["nodes"]}
        adjacency: dict[str, list[str]] = defaultdict(list)
        indegree: dict[str, int] = defaultdict(int)
        for raw in d["transitions"]:
            adjacency[raw["source_node_id"]].append(raw["target_node_id"])
            indegree[raw["target_node_id"]] += 1
        starts = [n.node_id for n in nodes.values() if n.public_reachable or indegree[n.node_id] == 0]
        chains: list[list[str]] = []
        for start in starts:
            q = deque([(start, [start])])
            while q:
                cur, path = q.popleft()
                next_nodes = adjacency.get(cur, [])
                if not next_nodes:
                    typed = [nodes[x].node_type for x in path if x in nodes]
                    if any(t in {NodeType.PROXY, NodeType.GATEWAY} for t in typed):
                        chains.append(path)
                    continue
                if len(path) >= 12:
                    continue
                for nxt in next_nodes:
                    if nxt not in path:
                        q.append((nxt, path + [nxt]))
        unique=[]
        for chain in chains:
            if chain not in unique:
                unique.append(chain)
        return unique

    def identity_transformations(self) -> list[dict[str, Any]]:
        out=[]
        for raw in self.store.load()["transitions"]:
            t=Transition.model_validate(raw)
            if t.data_type.lower() not in {"identity","header","jwt","token","credential"}: continue
            out.append({"transition_id":t.transition_id,"from":t.source_node_id,"to":t.target_node_id,"input":t.input_name,"output":t.output_name,"transformation":t.transformation,"verified":t.verified,"evidence_ids":t.evidence_ids,"provenance_preserved": bool(t.metadata.get("provenance_preserved", t.verified is True))})
        return out

    def trust_mutation_diff(self, source_a: str, source_b: str, target: str) -> dict[str, Any]:
        paths_a = self.paths(source_a, target)
        paths_b = self.paths(source_b, target)
        d = self.store.load()
        transitions = [Transition.model_validate(x) for x in d["transitions"]]
        def transitions_for(paths: list[list[str]]) -> list[dict[str, Any]]:
            pairs={(p[i],p[i+1]) for p in paths for i in range(len(p)-1)}
            return [t.model_dump(mode="json") for t in transitions if (t.source_node_id,t.target_node_id) in pairs]
        a = transitions_for(paths_a)
        b = transitions_for(paths_b)
        sig=lambda xs:{(x["data_type"],x.get("input_name"),x.get("output_name"),x.get("verified")) for x in xs}
        return {"source_a":source_a,"source_b":source_b,"target":target,"paths_a":paths_a,"paths_b":paths_b,"only_a":[list(x) for x in sorted(sig(a)-sig(b), key=str)],"only_b":[list(x) for x in sorted(sig(b)-sig(a), key=str)],"status":"HYPOTHESIS" if sig(a)!=sig(b) else "OBSERVED_EQUIVALENCE","note":"Differences describe observed/modelled trust transformations, not exploitability."}

    def jwt_metadata(self, claims: dict[str, Any]) -> dict[str, Any]:
        allowed={"iss","aud","sub","scope","roles","role","azp","client_id","typ"}
        return {k:claims[k] for k in sorted(allowed.intersection(claims))}

    def header_provenance(self, header_name: str) -> dict[str, Any]:
        name = header_name.casefold()
        transitions = [Transition.model_validate(x) for x in self.store.load()["transitions"]]
        matches=[t for t in transitions if (t.input_name or "").casefold()==name or (t.output_name or "").casefold()==name]
        return {"header":header_name,"observations":[{"transition_id":t.transition_id,"source":t.source_node_id,"target":t.target_node_id,"input":t.input_name,"output":t.output_name,"transformation":t.transformation,"verified":t.verified,"evidence_ids":t.evidence_ids} for t in matches],"confidence":"HIGH" if len(matches)>=2 and all(t.evidence_ids for t in matches) else ("MEDIUM" if matches else "UNKNOWN")}

    def contradictions(self) -> list[dict[str, Any]]:
        d = self.store.load()
        nodes = {x["node_id"]: Node.model_validate(x) for x in d["nodes"]}
        out = []
        for raw in d["assertions"]:
            a = TrustAssertion.model_validate(raw)
            node = nodes.get(a.node_id)
            if node is None: continue
            statement=a.statement.casefold()
            if node.public_reachable and any(term in statement for term in ("internal only","internal-only","not publicly reachable","only internal")):
                out.append({"assertion_id":a.assertion_id,"node_id":a.node_id,"status":"CONTRADICTED","assertion":a.statement,"counter_evidence":["Node is modeled/observed as public_reachable."],"evidence_ids":a.evidence_ids})
        return out

    def direct_origin_paths(self) -> list[dict[str, Any]]:
        d = self.store.load()
        nodes = {x["node_id"]: Node.model_validate(x) for x in d["nodes"]}
        results = []
        gateways={n.node_id for n in nodes.values() if n.node_type in {NodeType.PROXY,NodeType.GATEWAY}}
        for target in nodes.values():
            if target.node_type != NodeType.SERVICE: continue
            normal = []; alternate = []
            for source in nodes.values():
                if not source.public_reachable or source.node_id == target.node_id: continue
                for path in self.paths(source.node_id,target.node_id):
                    if any(x in gateways for x in path[1:-1]): normal.append(path)
                    else: alternate.append(path)
            if normal and alternate:
                results.append({"target":target.node_id,"normal_paths":normal,"alternate_paths":alternate,"status":"HYPOTHESIS","assumption":"Gateway-only reachability may be inconsistent with observed/modelled alternate path."})
        return results

    def compare(self, node_a: str, node_b: str) -> dict[str, Any]:
        d = self.store.load()
        def incoming(node_id: str) -> list[dict[str, Any]]:
            return [x for x in d["transitions"] if x["target_node_id"] == node_id]
        return {"node_a": node_a, "node_b": node_b, "incoming_a": incoming(node_a), "incoming_b": incoming(node_b)}
