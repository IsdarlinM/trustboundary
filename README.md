# TrustBoundary Mapper

```text
TrustBoundary Mapper
imr :: v0.3.1
```

Evidence-native identity, trust-transition and trust-assumption modeling.

> **AI proposes. Evidence proves. Humans control.**

## Implemented

- proxy/gateway chain reconstruction and identity transformation graph;
- architecture reconstruction with evidence/status/confidence per edge;
- identity provenance showing origin, transformation, validator and consumer;
- trust mutation diff, JWT/header provenance, contradiction and direct-origin path analysis;
- mTLS/SPIFFE metadata modeling without storing private keys;
- declarative Kubernetes/Istio/Envoy and import-only cloud architecture adapters;
- reusable trust assertions with conservative `UNKNOWN`, `INFERRED` and `HYPOTHESIS` semantics;
- shared SRIC 0.4.1 workspace, graph, jobs/SSE, evidence lineage, notebook/search and confidence calibration;
- local API/Web UI, CLI and offline demo.

## Architecture evidence layers in v0.3.1

TrustBoundary now separates `DECLARED`, `CONFIGURED` and `OBSERVED` trust paths. Differences produce configuration, runtime or identity-transformation drift hypotheses. Missing or contradictory layers remain `UNKNOWN`. Agreement only describes the sampled path and does not prove every route or deployment behaves identically.

Forwarding headers are normalized case-insensitively while duplicate and conflicting values are preserved. The mapper does not silently decide precedence between `Forwarded` and `X-Forwarded-*`, infer a trusted proxy count or assume append/replace behavior. Header ambiguity is evidence requiring configuration or runtime confirmation, not proof of exploitation.

## Quickstart

```bash
trustboundary doctor
trustboundary demo --workspace demo
trustboundary graph demo
trustboundary assumptions demo
trustboundary web demo
```

## Local release gate

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The complete machine-readable report is written to `build/release-evidence/release-gate.json`. A release requires `PASS` for the exact commit.

Inference never establishes exploitability. All imported content is untrusted data, and active actions remain behind SRIC Scope/Policy/Rate/Approval controls. Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
