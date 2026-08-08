# Test Evidence — TrustBoundary v0.5.0 Release Candidate

## Release-candidate review — 2026-08-08

The `agent/release-0.5.0` branch contains the TrustBoundary 0.5 changes under review:

- SRIC 0.5 compatibility;
- declarative trust invariants for identity verification, client-header stripping, transformations and provenance;
- automated results structurally limited to `OBSERVED`, `HYPOTHESIS` or `UNKNOWN`;
- evidence, counter-evidence and missing-evidence reporting;
- 0.5 regression tests and standardized release-evidence gate v2.

## Fresh execution status

**THE COMPLETE v0.5.0 RELEASE GATE HAS NOT BEEN EXECUTED SUCCESSFULLY FOR THIS BRANCH.**

The private repository cannot be mounted as a complete local checkout in this runtime. GitHub Actions currently ends in `startup_failure` before any test job starts; this is an infrastructure blocker, not test evidence.

## Required release evidence

Run from sibling 0.5 checkouts:

```bash
python sric-core/scripts/release-ecosystem.py --root .
```

Do not merge/tag TrustBoundary 0.5 until its exact-commit `release-gate.json` and the cross-product `ecosystem-release-gate.json` both report `PASS`.

Previous 0.3.x evidence remains a historical regression baseline only.
