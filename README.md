# TrustBoundary Mapper

```text
TrustBoundary Mapper :: v0.5.4
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
- signed update flow with safe same-version `update --force` reinstall support;
- Web Command Console with exact public CLI command-tree parity and real-time jobs;
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

Interactive terminals display a compact subdued-green banner ordered as `TrustBoundary Mapper :: v0.5.4`, `Developer: IsdarlinM`, then the trust/identity-flow purpose statement. Use `trustboundary --no-color COMMAND`, `trustboundary COMMAND --no-color`, or `NO_COLOR=1` for plain terminal presentation. The banner is emitted to interactive stderr so JSON and redirected stdout remain clean. See `docs/cli-presentation.md`.

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

The responsive local Web UI presents trust graphs, identity/trust evidence and analysis surfaces. `/console` adds the Web Command Console, whose catalog is generated from `trustboundary.cli_all`; a standalone test requires the Web and CLI command-path sets to be exactly equal.

The console is **not an arbitrary operating-system web shell**. It invokes only the fixed SRIC runner with `shell=False`, disabled stdin and a structured argv array. Mutating commands require explicit approval; Scope/Policy and evidence semantics remain authoritative. See `docs/web/cli-parity.md`.

## Signed updates

The updater accepts only an Ed25519-signed manifest and a SHA-256 verified wheel. Configure `TRUSTBOUNDARY_RELEASE_MANIFEST_URL` plus `TRUSTBOUNDARY_RELEASE_PUBLIC_KEY`, or pass `--manifest` and `--public-key`.

```bash
trustboundary update --check
trustboundary update
trustboundary update --force
```

`--force` reinstalls the selected signed release even when that exact version is already installed. It may install a newer signed version but never downgrades; `--check` and `--force` cannot be combined. No unsigned or blind `git pull` fallback is used. Until the official signed release channel is published, release-channel configuration remains explicit.

## Validation gates

```bash
python -m sric.standalone_gate --root .
python scripts/release-gate.py
```

Evidence is written below `build/release-evidence/`; PASS must correspond to the exact source commit.

## Uninstall

```bash
./scripts/uninstall-linux.sh
```

The runtime and command shim are removed while workspaces, configuration and evidence under `~/.trustboundary/` are preserved.

All imported content is untrusted data. Active actions remain behind SRIC Scope/Policy/Rate/Approval controls. Telemetry, cloud AI and external uploads are OFF by default. Apache-2.0.
