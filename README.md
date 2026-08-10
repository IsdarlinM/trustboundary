# TrustBoundary Mapper

```text
TrustBoundary Mapper :: v0.5.14
Developer: IsdarlinM

Map identity flows, trust transitions, assumptions, and evidence.
```

Evidence-native identity, trust-transition and trust-assumption modeling.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

TrustBoundary Mapper is independently installable and independently useful. It depends on **SRIC Core >=0.5.14,<0.6** for shared evidence, policy, workspaces, graph and Web/runtime primitives; ReproSec, AuthTwin, FossilScope and Exposure DNA are optional integrations, never startup requirements.

```bash
trustboundary doctor --json
trustboundary capabilities
```

## Implemented

- proxy/gateway chain reconstruction and identity transformation graph;
- architecture reconstruction with evidence/status/confidence per edge;
- identity provenance showing origin, transformation, validator and consumer;
- trust mutation diff, JWT/header provenance, contradiction and direct-origin path analysis;
- mTLS/SPIFFE metadata modeling without storing private keys;
- declarative Kubernetes/Istio/Envoy and import-only cloud architecture adapters;
- reusable trust assertions/invariants with conservative `UNKNOWN`, `INFERRED` and `HYPOTHESIS` semantics;
- SRIC workspace, graph, jobs/SSE, evidence lineage, notebook/search and confidence primitives;
- local API/Web UI, CLI and offline demo;
- zero-config official update flow with rollback and first-party runtime repair;
- exact SRIC version/module diagnostics in `doctor` and `/api/v1/runtime-compatibility`;
- shared **Sentinel Forge Security Workspace** with desktop product rail, Operations Library, dedicated Operation Workspace, separate execution evidence/output and full-width Recent Activity;
- professional offline Segoe UI Variable/Aptos/system typography and Cascadia Code/SFMono/Consolas evidence output with a restrained graphite/slate + teal palette;
- checkboxes/tri-state selectors for flags, combo/select controls for closed choices, numeric/path controls, repeated-value controls and protected sensitive fields;
- JSON-safe shared Web capability catalog generation with choice/bound/path metadata;
- structured redacted HTTP 503 handling when capability-catalog construction itself fails;
- bounded Web child termination/reaping and short-lived retired-job retention for active SSE/status readers;
- shared operational exception containment and persisted Job Engine secret redaction;
- shared-route CSP permitting same-origin Security Workspace CSS/JS while retaining restrictive object/base/frame policies;
- lazy shared-Web loading and actionable degraded `/workbench` 503 behavior so a missing shared UI module does not crash every CLI command;
- fixed-runner execution with exact CLI-tree parity and real-time jobs while keeping free-form command/argv entry out of the user interface;
- professional Rich/Typer terminal presentation with `--no-color` support.

## Evidence semantics

TrustBoundary separates `DECLARED`, `CONFIGURED` and `OBSERVED` trust paths. Differences produce hypotheses, not exploitation claims. Missing or contradictory layers remain `UNKNOWN`. A violated trust invariant can become `HYPOTHESIS`; automated analysis cannot create `VALIDATED` exploitability.

## Standalone install and repair

Linux / Termux:

```bash
./scripts/install-linux.sh
trustboundary doctor --json
trustboundary capabilities
```

Windows:

```cmd
scripts\install-windows.cmd
trustboundary doctor --json
trustboundary capabilities
```

The normal installer pins SRIC Core to immutable GitHub-verified commit `3c5d1e0eff2584d069843a5234d9d8a0357718b9` and resolves that explicit first-party source in the same pip transaction as TrustBoundary. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces and evidence. It validates host Python and any existing runtime interpreter; a stale, incomplete or broken environment rebuilds only `~/.trustboundary/venv`. It bootstraps `pip`, `setuptools` and `wheel`, resolves constrained TrustBoundary plus the explicit SRIC source, runs `pip check`, verifies `sric.web_console`, `sric.web_workbench`, `sric.web_security_workspace`, `sric.web_catalog` and `sric.web_runtime`, requires SRIC `>=0.5.14,<0.6`, and runs doctor/capability plus `--help`, `-h` and `help` smokes.

Installer-internal smokes use `SENTINEL_BANNER=never` and a temporary validation log. Successful installation does not repeat the TrustBoundary banner; captured diagnostics are printed if validation fails.

On Termux, a writable `$PREFIX/bin` already present in `PATH` is preferred so `trustboundary` is immediately reachable. Standard Linux falls back to `~/.local/bin`. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`; any Python 3 interpreter satisfying `>=3.11` is accepted.

## CLI presentation

Interactive terminals display `TrustBoundary Mapper :: v0.5.14`, `Developer: IsdarlinM`, then the trust/identity-flow purpose statement. Use `trustboundary --no-color COMMAND`, `trustboundary COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

The help contract covers `trustboundary --help`, `trustboundary -h`, `trustboundary help`, `trustboundary COMMAND --help`, `trustboundary COMMAND -h` and `trustboundary COMMAND help`.

Unexpected operational exceptions are redacted/contained by SRIC. `SENTINEL_DEBUG=1` is an explicit developer-only opt-in for raw local exception propagation.

## Quickstart

```bash
trustboundary doctor --json
trustboundary capabilities
trustboundary demo --workspace demo
trustboundary graph demo
trustboundary assumptions demo
trustboundary web demo
```

## Web and API

The native dashboard remains a quick trust-graph view. `/workbench` is the primary **Sentinel Forge Security Workspace** and is generated from `trustboundary.cli_all`, representing every public capability and ordered CLI parameter through structured responsive controls. `/console` is retained only as a compatibility alias that opens `/workbench`; it is not an argv-oriented user interface. `/api/v1/runtime-compatibility` exposes exact shared-runtime status.

The desktop Security Workspace is organized as a Sentinel Forge product rail plus a two-column Operations Library + Operation Workspace. Recent Activity sits below the main work area instead of consuming a permanent third column. Configuration, approval and evidence/output are separate surfaces; mobile collapses to guided Operations / Configure / Activity views.

SRIC 0.5.14 normalizes command metadata to deterministic JSON-safe primitives and includes choice, bound and path semantics so the browser can render appropriate HTML controls without duplicating product behavior. Shared UI assets are same-origin and require no external fonts or CDN resources.

Users do not type CLI command paths, option names, flags or free-form argv. Structured control values are serialized only as an internal transport detail to the fixed SRIC runner. Execution uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Scope/Policy/Rate/Approval and evidence semantics remain authoritative; no Web action can turn an inference into `VALIDATED` exploitability without evidence.

## Updates

```bash
trustboundary update --check
trustboundary update
trustboundary update --force
```

Supported stale SRIC runtimes are advanced through fixed immutable GitHub-signature-verified snapshots one release at a time from 0.5.5 through the 0.5.14 floor. The 0.5.13 -> 0.5.14 transition introduces the shared Security Workspace while retaining the fixed runner and existing catalog/runtime compatibility layer. No blind `git pull` fallback is used.

## Validation gates

```bash
python -m pytest -q tests/e2e/test_all_commands_dispatch_v0514.py
python -m pytest -q tests/e2e/test_security_workspace_v0514.py
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The command gate enumerates every public TrustBoundary leaf command and dispatches it through real Typer parsing/validation with network/server/update behavior kept offline. Existing deeper unit/integration/E2E/security suites cover trust graphs, assumptions, proxy chains, identity transformations/provenance, contradictions, direct-origin paths, headers, mTLS/SPIFFE, imports, native dashboard routes and conservative invariant semantics.

`TEST_EVIDENCE.md` is authoritative for what actually executed. A hosted job that never starts its steps is not treated as PASS.

## Uninstall

Linux / Termux:

```bash
./scripts/uninstall-linux.sh
```

Windows:

```cmd
scripts\uninstall-windows.cmd
```

The runtime and command shim are removed while workspaces, configuration and evidence under `~/.trustboundary/` / `%USERPROFILE%\.trustboundary` are preserved.

All imported content is untrusted data. Active actions remain behind SRIC Scope/Policy/Rate/Approval controls. Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
