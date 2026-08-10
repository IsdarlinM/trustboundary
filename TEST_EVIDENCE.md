# Test Evidence — TrustBoundary v0.5.12 Candidate

## Candidate review — 2026-08-10

TrustBoundary 0.5.12 aligns package metadata, runtime lock, bootstrap, `doctor`, Linux/Termux installer and Windows installer to SRIC Core `>=0.5.12,<0.6` and pins signed SRIC main commit `4dd0ad417e55fc76fb67d582ec50234bffff2876`.

Candidate regressions verify the exact first-party pin/lock, required `sric.web_console`, `sric.web_workbench`, `sric.web_catalog` and `sric.web_runtime` modules, the fixed signed 0.5.5→0.5.12 sequential repair chain, same-version 0.5.12 repair, degraded Workbench 503 behavior, every public CLI help form and exact ordered CLI/Web parameter parity. Existing suites cover trust graphs, identity provenance, headers, assumptions, imports, invariants, native API/Web surfaces and conservative `UNKNOWN`/`HYPOTHESIS` semantics.

## Executed focused shared-runtime evidence

The SRIC Core 0.5.12 runtime used by this candidate was exercised in a focused local harness. An initial `3 passed, 1 failed` run exposed a background-reaper return-code race; after correction the targeted harness completed:

```text
4 passed in 0.19s
```

The four checks covered redacted catalog HTTP 503 behavior, terminal-job/SSE retention, final-wait background reaping and Job Engine persistence redaction. This is shared-runtime evidence only, not a full TrustBoundary repository/platform/browser PASS.

## Exact-commit gate status

**THE COMPLETE v0.5.12 TRUSTBOUNDARY TEST/RELEASE GATES HAVE NOT EXECUTED.**

GitHub-hosted jobs currently cannot allocate runners because the account is locked due to a billing issue; observed jobs have `runner_id=0` and `steps=[]`. The maintenance execution container also cannot resolve `github.com`, so it cannot materialize a full checkout as a substitute. Zero-step workflows and static review are not PASS evidence.

## Required exact-commit evidence before release completion

```bash
python -m sric.standalone_gate --root trustboundary
python sric-core/scripts/release-standalone-ecosystem.py --root .
python trustboundary/scripts/release-gate.py
python sric-core/scripts/release-ecosystem.py --root .
```

The Definition of Done still requires successful unit/integration/E2E/security/fuzz execution; every CLI command/help alias; exact CLI/Web parity; Console/Workbench/native Web pages, assets, buttons/forms, submission/cancellation/approval/SSE behavior; documented GET/POST API valid/invalid cases; clean Linux/Termux and Windows install/repair; update/rollback preservation; responsive-browser/console review; secret/dependency/SAST/SBOM/build checks; and ecosystem execution against exact final commits.

The project owner explicitly requested integration of the corrected candidate to `main`; that integration must not be described as proof that the externally blocked full gates passed.
