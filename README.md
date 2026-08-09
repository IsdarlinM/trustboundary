# TrustBoundary Mapper

```text
TrustBoundary Mapper :: v0.5.6
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
- zero-config official update flow with safe same-version `update --force` reinstall support;
- full Web Feature Workbench with every public TrustBoundary CLI command and argument represented as structured responsive controls;
- advanced Web Command Console with exact public CLI command-tree parity and real-time jobs;
- professional Rich/Typer terminal presentation with subdued green banner and `--no-color` support.

## Evidence semantics

TrustBoundary separates `DECLARED`, `CONFIGURED` and `OBSERVED` trust paths. Differences produce hypotheses, not exploitation claims. Missing or contradictory layers remain `UNKNOWN`. A violated trust invariant can become `HYPOTHESIS`; automated analysis cannot create `VALIDATED` exploitability.

## Standalone install

Linux:

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

The installer resolves SRIC automatically. `SRIC_CORE_SOURCE` is an explicit development/release-validation override only.

## CLI presentation

Interactive terminals display a compact subdued-green banner ordered as `TrustBoundary Mapper :: v0.5.6`, `Developer: IsdarlinM`, then the trust/identity-flow purpose statement. Use `trustboundary --no-color COMMAND`, `trustboundary COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation.

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

The native dashboard remains a quick trust-graph view and now exposes visible navigation to **All Features** (`/workbench`) and **Advanced Console** (`/console`). The Workbench is generated from `trustboundary.cli_all` and represents every public command and every ordered CLI parameter as structured responsive controls.

The Workbench is not an operating-system shell. Execution uses the fixed SRIC runner with `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Scope/Policy/Rate/Approval and evidence semantics remain authoritative; no Web action can turn an inference into `VALIDATED` exploitability without evidence.

## Updates

```bash
trustboundary update --check
trustboundary update
trustboundary update --force
```

The official path is zero-config. `--force` may reinstall the current official version or move forward, never downgrade. Custom `--manifest` plus `--public-key` remains an advanced signed-channel override.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

The 0.5.6 interface suite walks every public command with `--help`, verifies all options/required arguments, compares the complete ordered CLI parameter tree with the Workbench catalog, and smoke-tests native trust graph, assumptions, proxy-chain, transformation, contradiction and origin-path APIs. Destructive operations are gate-tested rather than executed solely for coverage.

Evidence is written below `build/release-evidence/`; PASS must correspond to the exact source commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime and command shim are removed while workspaces, configuration and evidence under `~/.trustboundary/` are preserved.

All imported content is untrusted data. Active actions remain behind SRIC Scope/Policy/Rate/Approval controls. Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
