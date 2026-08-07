# Test Evidence — TrustBoundary v0.3.1

## QA pass — 2026-08-07

Freshly executed in the current local runtime:

- Sentinel Forge cross-product high-risk regression matrix including TrustBoundary WebSocket trust-path logic: **7/7 matrix tests passed**;
- Python `compileall` over the reconstructed corrected modules: **PASS**;
- branch comparison against `main`: branch is ahead and **0 commits behind** at the time of this audit.

Current-source review and regression coverage include:

- declared/configured/observed trust-layer separation;
- duplicate/conflicting forwarding-header preservation;
- architecture import as untrusted data with no execution;
- identity provenance remaining `UNKNOWN` when incomplete;
- evidence required for every WebSocket trust observation;
- validator required for authentication transitions;
- pre-revocation message control required before post-revocation can become `HYPOTHESIS`;
- timezone-aware observations;
- repaired executable Python integration test that previously contained JSON `true`;
- WebSocket endpoint actually registered in vNext;
- complete CLI entrypoint registration for `websocket-trust`;
- recursive help-path coverage and controlled CLI errors;
- `trustboundary web` serving the workspace-bound vNext API and CSP-protected UI;
- public Python exports for WebSocket trust primitives.

## Current release-gate status

**FULL CURRENT REPOSITORY GATE NOT EXECUTABLE IN THIS RUNTIME.**

The private repository cannot be materialized as a complete local checkout from the connector, and Ruff, mypy, `build` and `pip-audit` are unavailable from the runtime/index. No GitHub Actions, Codespaces or paid/hosted GitHub execution was used.

Before treating v0.3.1 as a fully validated release, run the exact commit from a local sibling checkout:

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

## Previous validated baseline

The previous v0.3.0 state was recorded on 2026-07-22 with **20 pytest tests passed**, compileall/security scan/CLI help/synthetic smoke/build/isolated wheel smoke PASS. Those results are a historical baseline only.
