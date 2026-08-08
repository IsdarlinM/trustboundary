# Test Evidence — TrustBoundary v0.5.0 Release Candidate

## Release-candidate review — 2026-08-08

The `agent/release-0.5.0` branch contains:

- SRIC 0.5 compatibility with no mandatory sibling-product dependency;
- declarative trust invariants with `OBSERVED`, `HYPOTHESIS` or `UNKNOWN` outcomes;
- evidence, counter-evidence and missing-evidence reporting;
- `trustboundary capabilities` and `/api/v1/capabilities`;
- standalone CLI/API/Web tests and recursive help/parser contracts;
- Linux/Windows clean-install smoke definitions using only TrustBoundary + SRIC;
- Linux uninstall that preserves workspaces/configuration/evidence;
- standardized standalone and release-evidence gates.

## Fresh execution status

**THE COMPLETE v0.5.0 TEST/RELEASE GATES HAVE NOT EXECUTED SUCCESSFULLY FOR THIS BRANCH.**

The repository cannot be mounted as a complete local checkout in this runtime. The latest observed GitHub Actions run concluded `startup_failure` and exposed zero jobs. No pytest, installer, static-analysis or wheel result from that run is counted as evidence.

## Required exact-commit evidence

```bash
python -m sric.standalone_gate --root trustboundary
python sric-core/scripts/release-standalone-ecosystem.py --root .
python trustboundary/scripts/release-gate.py
python sric-core/scripts/release-ecosystem.py --root .
```

All gate layers must report PASS before merge/tag. Previous 0.3.x evidence remains a historical baseline only.
