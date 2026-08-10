# Changelog

## 0.5.10 - 2026-08-09
- Adopted signed SRIC Core 0.5.11 and its JSON-safe Web command catalog while preserving TrustBoundary evidence/provenance and conservative truth-state semantics.
- Kept normal Linux/Termux/Windows installation atomic and idempotent with no `--force-reinstall`; forced reinstall remains explicit to repair/update workflows.
- Installer-internal doctor/capability/help smokes now suppress banners with `SENTINEL_BANNER=never` and emit captured diagnostics only on failure.
- Added exact SRIC pin/lock, quiet-installer and HTTP-200 Console/Workbench catalog regressions.

## 0.5.9 - 2026-08-09
- Hardened repair installation so obsolete, incomplete or broken Python environments rebuild only `~/.trustboundary/venv`, preserving trust workspaces, configuration and evidence.
- Termux now prefers a writable `$PREFIX/bin` already present in `PATH`, making `trustboundary` immediately reachable after installation.
- Windows PATH updates now use SRIC Core's registry-backed `sric.install_path` helper instead of `setx`, avoiding user-PATH truncation/rewrite hazards.
- Preserved the atomic TrustBoundary + explicit first-party SRIC resolver fix and updated the immutable SRIC pin/runtime lock to SRIC Core 0.5.10.
- Expanded installer regressions for venv-only repair, Termux path selection, safe Windows PATH handling, Python discovery, dependency integrity and help smokes.

## 0.5.8 - 2026-08-09
- Fixed clean/repair installation `ResolutionImpossible` when TrustBoundary depends on the first-party `sric-core` package distributed from an immutable GitHub snapshot rather than PyPI.
- Linux/Termux and Windows now resolve TrustBoundary plus the explicit SRIC source in one pip transaction; the installer no longer performs a product-only `--force-reinstall` that can make pip search the public index for `sric-core`.
- Updated the immutable first-party SRIC pin and runtime lock to SRIC Core 0.5.9.
- Fixed Linux PATH persistence so `.profile` does not inject literal quote characters into PATH.
- Fixed Windows Python discovery to accept any installed Python 3 runtime that satisfies `>=3.11` instead of requiring `py -3.11` specifically.
- Installers now bootstrap pip/setuptools/wheel, run `pip check`, import-probe shared Web modules, and smoke-test `--help`, `-h`, and `help` before reporting success.
- Added standalone regression coverage for the exact resolver topology, immutable SRIC pin, PATH quoting and Windows Python selection.

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
