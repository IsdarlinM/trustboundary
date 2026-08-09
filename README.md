# TrustBoundary Mapper

```text
TrustBoundary Mapper :: v0.5.9
Developer: IsdarlinM

Map identity flows, trust transitions, assumptions, and evidence.
```

Evidence-native identity, trust-transition and trust-assumption modeling.

> **AI proposes. Evidence proves. Humans control.**

## Standalone by design

TrustBoundary Mapper is independently installable and independently useful. It depends on SRIC Core 0.5.x for shared evidence, policy, workspaces and graph primitives; ReproSec, AuthTwin, FossilScope and Exposure DNA are optional integrations, never startup requirements.

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
- SRIC 0.5.x workspace, graph, jobs/SSE, evidence lineage, notebook/search and confidence primitives;
- local API/Web UI, CLI and offline demo;
- zero-config official update flow with same-version `update --force`, rollback and first-party runtime repair;
- exact SRIC version/module diagnostics in `doctor` and `/api/v1/runtime-compatibility`;
- full Web Feature Workbench with every public TrustBoundary CLI command and argument represented as structured responsive controls;
- lazy shared-Web loading and actionable degraded Workbench 503 behavior so a missing shared UI module does not crash every CLI command;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

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

The normal installer pins SRIC Core to an immutable GitHub commit and resolves that explicit first-party source **in the same pip transaction as TrustBoundary**. Because `sric-core` is intentionally not discovered from PyPI, the installer no longer runs a later product-only `--force-reinstall` that can trigger `ResolutionImpossible`. `SRIC_CORE_SOURCE=/path/to/sric-core` remains an explicit development/release-validation override.

The repair path preserves workspaces and evidence. It validates host Python and any existing runtime interpreter; a stale, incomplete or broken environment rebuilds only `~/.trustboundary/venv`. It bootstraps `pip`, `setuptools` and `wheel`, force-reinstalls constrained TrustBoundary plus the explicit SRIC source, runs `pip check`, verifies `sric.web_console` and `sric.web_workbench`, checks the supported SRIC version range, and runs doctor/capability plus `--help`, `-h` and `help` smokes.

On Termux, a writable `$PREFIX/bin` already present in `PATH` is preferred so `trustboundary` is immediately reachable. Standard Linux falls back to `~/.local/bin` and persists the canonical profile entry only when necessary. Windows uses SRIC's registry-backed `sric.install_path` helper instead of `setx`; any Python 3 interpreter satisfying `>=3.11` is accepted.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `TrustBoundary Mapper :: v0.5.9`, `Developer: IsdarlinM`, then the trust/identity-flow purpose statement. Use `trustboundary --no-color COMMAND`, `trustboundary COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

The help contract covers `trustboundary --help`, `trustboundary -h`, `trustboundary help`, `trustboundary COMMAND --help`, `trustboundary COMMAND -h` and `trustboundary COMMAND help`.

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

The native dashboard remains a quick trust-graph view and exposes visible navigation to **All Features** (`/workbench`) and **Advanced Console** (`/console`). The Workbench is generated from `trustboundary.cli_all` and represents every public command and every ordered CLI parameter as structured responsive controls. `/api/v1/runtime-compatibility` exposes exact shared-runtime status.

Shared Web modules are loaded lazily. A stale/corrupt SRIC therefore cannot make every TrustBoundary command fail merely because an optional shared UI module is missing; the native app remains reachable and the unavailable Workbench returns an actionable `RUNTIME_INCOMPATIBLE` 503.

The Workbench is not an operating-system shell. Execution uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Scope/Policy/Rate/Approval and evidence semantics remain authoritative; no Web action can turn an inference into `VALIDATED` exploitability without evidence.

## Updates

```bash
trustboundary update --check
trustboundary update
trustboundary update --force
```

For official updates, TrustBoundary verifies SRIC before updating the product. Supported stale 0.5.x cores are bridged through immutable GitHub-signature-verified historical snapshots to the compatible floor; a compatible-version core with missing required modules is force-reinstalled through the official channel. Custom/private `--manifest` plus `--public-key` updates remain explicit and do not silently switch the core channel.

The official path is zero-config. `--force` may reinstall the current official version or move forward, never downgrade, and no blind `git pull` fallback is used.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.9 installer regression verifies the unpublished-first-party resolver topology, immutable SRIC pin, runtime lock, venv-only repair, Termux `$PREFIX/bin`, safe Windows PATH handling, Python discovery and dependency/import/help smokes. Existing runtime/interface and unit/integration/E2E/security suites continue to cover trust graphs, assumptions, proxy chains, identity transformations/provenance, contradictions, direct-origin paths, headers, mTLS/SPIFFE, imports and conservative invariant semantics. Destructive operations are gate-tested rather than executed solely for coverage.

Evidence is written below `build/release-evidence/`; PASS must correspond to the exact source commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime and command shim are removed while workspaces, configuration and evidence under `~/.trustboundary/` are preserved.

All imported content is untrusted data. Active actions remain behind SRIC Scope/Policy/Rate/Approval controls. Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
