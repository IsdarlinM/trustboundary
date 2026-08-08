# Roadmap

## Current — 0.5.0 release candidate

Implemented in the 0.5 train:
- SRIC 0.5 integration.
- Declarative trust invariants for identity verification, client-header stripping, required transformations and provenance preservation.
- Conservative `OBSERVED`, `HYPOTHESIS` and `UNKNOWN` invariant outcomes with counter-evidence/missing-evidence reporting.
- CLI/API invariant evaluation surfaces and regression tests.
- `doctor` compatibility updated for SRIC 0.5 and coordinated release-evidence gate v2.

## Next hardening
- Provider-specific schema validation for gateways, load balancers, Kubernetes/service mesh and cloud imports.
- Deeper signed-header/token-exchange provenance and WebSocket trust paths.
- Rich architecture-version graph diff/visualization without active bypass attempts.
- Larger trust-invariant corpus with counterevidence-driven false-positive evaluation.
- Browser E2E, graph performance benchmarks and signed release attestations.

## 1.0
Stable trust schema/DSL, external architecture case studies and audited evidence-to-assumption workflow.
