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

def _walk_scalars(obj: Any) -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for value in obj.values(): out.extend(_walk_scalars(value))
    elif isinstance(obj, list):
        for value in obj: out.extend(_walk_scalars(value))
    elif isinstance(obj, (str,int,float,bool)): out.append(str(obj))
    return out

class ImportMixin:
    def import_platform_config(self, path: Path) -> dict[str, int]:
        """Import supplied Kubernetes/Istio/Envoy configuration without contacting a cluster."""
        import hashlib
        import json

        if not path.is_file() or path.is_symlink():
            raise ValueError("configuration must be a regular non-symlink file")
        if path.stat().st_size > MAX_IMPORT_BYTES:
            raise ValueError(f"configuration exceeds {MAX_IMPORT_BYTES} byte limit")
        text = path.read_text(encoding="utf-8")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ValueError("YAML import requires the optional 'yaml' extra (PyYAML)") from exc
            docs = list(yaml.safe_load_all(text))
            payload = docs if len(docs) > 1 else docs[0]

        objects: list[dict[str, Any]] = []
        if isinstance(payload, list):
            objects = [x for x in payload if isinstance(x, dict)]
        elif isinstance(payload, dict) and payload.get("kind") == "List" and isinstance(payload.get("items"), list):
            objects = [x for x in payload["items"] if isinstance(x, dict)]
        elif isinstance(payload, dict):
            objects = [payload]
        else:
            raise ValueError("unsupported platform configuration document")

        node_count = 0
        transition_count = 0

        def nid(prefix: str, name: str) -> str:
            return f"{prefix}-" + hashlib.sha256(name.encode()).hexdigest()[:10]

        def ensure(node: Node) -> None:
            nonlocal node_count
            existing = {x["node_id"] for x in self.store.load()["nodes"]}
            self.add_node(node)
            if node.node_id not in existing:
                node_count += 1

        for obj in objects:
            kind = str(obj.get("kind", ""))
            api_version = str(obj.get("apiVersion", ""))
            metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
            name = str(metadata.get("name", kind or "unnamed"))
            spec = obj.get("spec") if isinstance(obj.get("spec"), dict) else {}

            if kind == "Ingress":
                gateway_id = nid("ingress", name)
                ensure(Node(node_id=gateway_id, name=name, node_type=NodeType.GATEWAY, public_reachable=True, metadata={"platform": "kubernetes", "kind": kind}))
                rules = spec.get("rules") if isinstance(spec.get("rules"), list) else []
                backends: set[str] = set()
                default_backend = spec.get("defaultBackend") if isinstance(spec.get("defaultBackend"), dict) else None
                if default_backend:
                    svc = default_backend.get("service") if isinstance(default_backend.get("service"), dict) else {}
                    if svc.get("name"): backends.add(str(svc["name"]))
                for rule in rules:
                    http = rule.get("http") if isinstance(rule, dict) and isinstance(rule.get("http"), dict) else {}
                    paths = http.get("paths") if isinstance(http.get("paths"), list) else []
                    for path_item in paths:
                        backend = path_item.get("backend") if isinstance(path_item, dict) and isinstance(path_item.get("backend"), dict) else {}
                        service = backend.get("service") if isinstance(backend.get("service"), dict) else {}
                        if service.get("name"): backends.add(str(service["name"]))
                for svc_name in sorted(backends):
                    svc_id = nid("svc", svc_name)
                    ensure(Node(node_id=svc_id, name=svc_name, node_type=NodeType.SERVICE, metadata={"platform": "kubernetes"}))
                    self.add_transition(Transition(transition_id=nid("route", f"{gateway_id}:{svc_id}"), source_node_id=gateway_id, target_node_id=svc_id, data_type="network_path", verified=None, metadata={"source": "kubernetes_ingress", "provenance_preserved": False}))
                    transition_count += 1

            elif kind == "Service":
                ensure(Node(node_id=nid("svc", name), name=name, node_type=NodeType.SERVICE, metadata={"platform": "kubernetes", "kind": kind, "service_type": spec.get("type")}))

            elif "istio.io" in api_version and kind == "Gateway":
                ensure(Node(node_id=nid("istio-gw", name), name=name, node_type=NodeType.GATEWAY, public_reachable=True, metadata={"platform": "istio", "kind": kind}))

            elif "istio.io" in api_version and kind == "VirtualService":
                vs_id = nid("istio-vs", name)
                ensure(Node(node_id=vs_id, name=name, node_type=NodeType.GATEWAY, metadata={"platform": "istio", "kind": kind}))
                destinations: set[str] = set()
                for section in ("http", "tcp", "tls"):
                    routes = spec.get(section) if isinstance(spec.get(section), list) else []
                    for route_block in routes:
                        route_items = route_block.get("route") if isinstance(route_block, dict) and isinstance(route_block.get("route"), list) else []
                        for route in route_items:
                            dest = route.get("destination") if isinstance(route, dict) and isinstance(route.get("destination"), dict) else {}
                            if dest.get("host"): destinations.add(str(dest["host"]))
                for host in sorted(destinations):
                    svc_id = nid("svc", host)
                    ensure(Node(node_id=svc_id, name=host, node_type=NodeType.SERVICE, metadata={"platform": "istio"}))
                    self.add_transition(Transition(transition_id=nid("route", f"{vs_id}:{svc_id}"), source_node_id=vs_id, target_node_id=svc_id, data_type="network_path", verified=None, metadata={"source": "istio_virtualservice"}))
                    transition_count += 1

            elif "static_resources" in obj:
                envoy_id = nid("envoy", path.name)
                ensure(Node(node_id=envoy_id, name=f"Envoy:{path.name}", node_type=NodeType.PROXY, metadata={"platform": "envoy"}))
                static = obj.get("static_resources") if isinstance(obj.get("static_resources"), dict) else {}
                clusters = static.get("clusters") if isinstance(static.get("clusters"), list) else []
                for cluster in clusters:
                    cluster_name = str(cluster.get("name", "unnamed")) if isinstance(cluster, dict) else "unnamed"
                    svc_id = nid("cluster", cluster_name)
                    ensure(Node(node_id=svc_id, name=cluster_name, node_type=NodeType.SERVICE, metadata={"platform": "envoy", "kind": "cluster"}))
                    self.add_transition(Transition(transition_id=nid("route", f"{envoy_id}:{svc_id}"), source_node_id=envoy_id, target_node_id=svc_id, data_type="network_path", verified=None, metadata={"source": "envoy_config"}))
                    transition_count += 1

        return {"nodes": node_count, "transitions": transition_count, "mode": "IMPORT_ONLY"}

    def parse_assertion_dsl(self, text: str) -> TrustAssertion:
        """Parse a deliberately small auditable trust-assertion DSL."""
        fields: dict[str, str] = {}
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition(" ")
            if not sep:
                raise ValueError(f"invalid assertion DSL line: {line}")
            key = key.upper()
            if key not in {"ASSERTION", "NODE", "STATEMENT", "BASIS", "EVIDENCE"}:
                raise ValueError(f"unsupported assertion DSL keyword: {key}")
            fields[key] = value.strip()
        missing = [k for k in ("ASSERTION", "NODE", "STATEMENT", "BASIS") if not fields.get(k)]
        if missing:
            raise ValueError(f"missing assertion DSL fields: {', '.join(missing)}")
        evidence = [x.strip() for x in fields.get("EVIDENCE", "").split(",") if x.strip()]
        assertion = TrustAssertion(assertion_id=fields["ASSERTION"], node_id=fields["NODE"], statement=fields["STATEMENT"], basis=fields["BASIS"], evidence_ids=evidence, metadata={"source": "trust_assertion_dsl"})
        self.add_assertion(assertion)
        return assertion

    def import_har(self, path: Path) -> dict[str, int]:
        """Import HAR metadata as trust observations without replaying any traffic."""
        from urllib.parse import urlsplit
        import hashlib

        payload = _load_json_file(path)
        entries = payload.get("log", {}).get("entries", []) if isinstance(payload, dict) else []
        if not isinstance(entries, list):
            raise ValueError("HAR log.entries must be a list")
        if not any(x.get("node_id") == "client" for x in self.store.load()["nodes"]):
            self.add_node(Node(node_id="client", name="Observed Client", node_type=NodeType.ZONE, public_reachable=True))
        transitions = 0
        hosts: set[str] = set()
        interesting = {"authorization", "x-forwarded-for", "x-real-ip", "x-user-id", "x-auth-user", "cf-connecting-ip", "forwarded", "via"}
        for entry in entries:
            req = entry.get("request", {})
            url = str(req.get("url", ""))
            host = urlsplit(url).hostname
            if not host:
                continue
            node_id = "host-" + hashlib.sha256(host.encode()).hexdigest()[:12]
            if host not in hosts:
                self.add_node(Node(node_id=node_id, name=host, node_type=NodeType.SERVICE, public_reachable=True, metadata={"source": "HAR"}))
                hosts.add(host)
            for header in req.get("headers", []):
                name = str(header.get("name", ""))
                if name.lower() not in interesting and not name.lower().startswith("x-user-"):
                    continue
                tid = "HAR-" + hashlib.sha256(f"{entry.get('startedDateTime')}:{host}:{name}".encode()).hexdigest()[:12]
                self.add_transition(Transition(transition_id=tid, source_node_id="client", target_node_id=node_id, data_type="header" if name.lower() != "authorization" else "token", input_name=name, verified=None, evidence_ids=[tid], metadata={"source": "HAR", "client_controlled_observation": True}))
                transitions += 1
        return {"hosts": len(hosts), "transitions": transitions}
