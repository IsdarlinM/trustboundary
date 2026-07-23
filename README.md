# TrustBoundary Mapper

```text
TrustBoundary Mapper
imr :: v0.3.0
```

Evidence-native identity, trust-transition and trust-assumption modeling.

> **AI proposes. Evidence proves. Humans control.**

## v0.3.0
- proxy/gateway chain reconstruction and identity transformation graph;
- architecture reconstruction v2 with evidence/status/confidence per edge;
- identity provenance showing origin, transformation, validator and consumer;
- trust mutation diff, JWT/header provenance, contradiction and direct-origin path analysis;
- mTLS/SPIFFE metadata modeling without storing private keys;
- declarative Kubernetes/Istio/Envoy and import-only cloud architecture adapters;
- reusable trust assertion library with conservative `UNKNOWN`/`INFERRED`/`HYPOTHESIS` semantics;
- shared SRIC 0.4 workspace, graph, jobs/SSE, evidence lineage and notebook/search integration;
- local API/Web UI, CLI, offline demo and signed update primitive.

Inference never establishes exploitability. All imported content is untrusted data, and active actions remain behind SRIC Scope/Policy/Rate/Approval controls.

## Quickstart
```bash
trustboundary doctor
trustboundary demo --workspace demo
trustboundary graph demo
trustboundary assumptions demo
trustboundary web demo
```

Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
