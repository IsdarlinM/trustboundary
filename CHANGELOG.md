# Changelog

## 0.5.7 - 2026-08-09
- Fixed first-party runtime drift that could install a newer TrustBoundary beside an older SRIC and fail on shared Web-module imports before command dispatch.
- Added exact SRIC distribution/module diagnostics, lazy shared-Web imports, `/api/v1/runtime-compatibility`, and actionable degraded Workbench 503 responses.
- Official updates repair supported stale/corrupt SRIC 0.5.x runtimes through immutable GitHub-signature-verified transition snapshots before updating TrustBoundary.
- Linux/Windows installers now force-reinstall pinned first-party dependencies and TrustBoundary, run `pip check`, import-probe Web Console/Workbench and execute doctor/capability/help smokes.
- Added regressions for stale/missing Workbench runtimes, signed transition chain, same-version repair, every public CLI help form and exact ordered CLI/Web parameter parity while preserving evidence/provenance semantics.
- New installs pin signed SRIC Core 0.5.8.

## 0.5.6 - 2026-08-09
- Added the full Web Feature Workbench at `/workbench`, generated from `trustboundary.cli_all`, with structured responsive controls for every public CLI command and argument.
- Added visible Dashboard / All Features / Advanced Console navigation to the native trust-graph Web surface.
- Preserved evidence/provenance semantics and Scope/Policy/Rate/Approval controls; Web execution cannot promote an inference or hypothesis to `VALIDATED` exploitability.
- Updated SRIC Core floor, runtime lock and exact first-party pin to the signed SRIC 0.5.6 Workbench release.
- Added exhaustive CLI help/argument-to-Web parity tests and native trust-surface API smoke coverage.

## 0.5.5 - 2026-08-08
- Made the official TrustBoundary updater zero-config: `trustboundary update`, `trustboundary update --check`, and `trustboundary update --force` no longer require user-supplied manifest/key configuration.
- Delegated official update trust and immutable GitHub signed-commit validation to SRIC Core 0.5.5 while preserving same-version force reinstall and downgrade rejection.
- Kept `--manifest` plus `--public-key` as an explicit advanced custom/private-channel override.
- Updated the SRIC Core runtime floor, lock, and exact first-party pin to the signed SRIC 0.5.5 release commit.
- Added standalone regression coverage proving `trustboundary update --force` selects the official channel with no manifest/key.

## 0.5.4 - 2026-08-08
- Added the SRIC Web Command Console at `/console`, exposing the complete installed `trustboundary.cli_all` command tree without an operating-system shell.
- Added exact Web-catalog-to-CLI-tree regression coverage so future public CLI commands cannot silently disappear from the Web console.
- Preserved TrustBoundary evidence/provenance semantics and Scope/Policy controls; Web invocation cannot promote a hypothesis to a validated finding.
- Added fixed-runner `shell=False` execution, explicit mutation approval, secret redaction, cancellable jobs and real-time SSE output through SRIC Core 0.5.4.
- Updated package/runtime dependency metadata and the exact SRIC first-party pin to the 0.5.4 Web parity snapshot.

## 0.5.3 - 2026-08-08
- Added `trustboundary update --force` for explicit same-version reinstall of a trusted signed release using pip `--force-reinstall`.
- Preserved Ed25519 manifest verification, SHA-256 wheel verification, state backup and rollback behavior.
- `--force` may install the same or a newer signed release, never an older release; SemVer prerelease precedence is enforced by SRIC Core.
- `--check` and `--force` are mutually exclusive.
- Updated the SRIC Core runtime floor, lock and exact first-party source pin to 0.5.3.
- Added standalone regression coverage for the public `--force` CLI contract.

## 0.5.2 - 2026-08-08
- Added a subdued green interactive CLI banner ordered as `TrustBoundary Mapper :: v0.5.2`, `Developer: IsdarlinM`, then the product description.
- Added colorized Typer/Rich command help plus global `--no-color` and `NO_COLOR` support.
- Kept banner output on interactive stderr so JSON, graph output and automation stdout remain clean.
- Added CLI branding regression tests and documentation.
- Updated the SRIC Core runtime floor, lock and first-party source pin to 0.5.2.

## 0.5.1 - 2026-08-08
- Fixed clean installation when `sric-core` is not published on PyPI.
- Added a first-party dependency manifest pinned to the exact SRIC Core 0.5.1 GitHub commit.
- Windows and Linux installers now bootstrap first-party dependencies before TrustBoundary and its third-party runtime dependencies.
- Preserved `SRIC_CORE_SOURCE` as an explicit development override.
- Updated the SRIC dependency floor/runtime lock to 0.5.1 and added installer contract regression coverage.

## 0.5.0 - 2026-08-08
- Added declarative trust invariants for verified identity, client-header stripping, required transformations and provenance preservation.
- Added evidence-linked invariant results with explicit `OBSERVED`, `HYPOTHESIS` or `UNKNOWN` outcomes; automated invariant evaluation cannot create `VALIDATED` results.
- Added conservative counter-evidence and missing-evidence reporting for unverified identity and header-sanitization assumptions.
- Updated SRIC compatibility to the Sentinel Forge 0.5 release train.
- Added standalone capability discovery with no mandatory sibling-product dependencies.
- Reworked Linux/Windows installation to resolve SRIC 0.5 automatically and removed adjacent-repository auto-discovery.
- Added standalone CLI/API/Web contracts, recursive help/parser tests, clean-install smokes and data-preserving Linux uninstall behavior.
- Added regression tests for verified/unverified identity flows and client-supplied identity header preservation.

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
