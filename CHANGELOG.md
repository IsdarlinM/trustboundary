# Changelog

## 0.3.1 - 2026-08-06
- Added explicit `DECLARED`, `CONFIGURED` and `OBSERVED` architecture/trust layers.
- Added conservative configuration, runtime and identity-transformation drift analysis.
- Missing or contradictory layers remain `UNKNOWN`; drift remains `HYPOTHESIS` and never establishes exploitability.
- Added case-insensitive forwarding-header normalization that preserves duplicate and conflicting values instead of silently choosing one.
- Added explicit limitations for `Forwarded`/`X-Forwarded-For` coexistence, trusted proxy count and append/replace semantics.
- Added tests for incomplete layers, contradictory runtime paths, validator drift and header ambiguity.
- Replaced hosted GitHub Actions/Dependabot automation with a local reproducible release gate.

## 0.3.0 - 2026-07-22
- Added architecture reconstruction v2 with evidence/status/confidence per inferred trust edge.
- Added identity provenance, mTLS/SPIFFE metadata modeling without private-key storage, cloud import-only adapters and trust assertion library.
- Expanded trust mutation comparison and conservative assertion evaluation.
- Upgraded to shared SRIC 0.4 workspace namespaces and graph/jobs/lineage primitives.
