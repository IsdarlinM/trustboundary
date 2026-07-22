# TrustBoundary Mapper

```text
TrustBoundary Mapper
imr :: v0.2.0
```

Models trust zones, proxies/gateways/services, identity-bearing data and transformations to make implicit trust assumptions explainable.

> **AI proposes. Evidence proves. Humans control.**

## What works in v0.2.0

- architecture nodes for zones, services, proxies, gateways, identities, credentials and networks;
- typed transitions for headers/tokens/JWT/identity transformations with evidence and verification state;
- trust assertions, path enumeration, identity-flow views and incoming-path comparison;
- conservative inference of unverified identity transitions and network-location trust assumptions;
- every candidate includes evidence, counter-evidence, confidence reasoning and limitations;
- architecture JSON import plus passive HAR metadata import (no replay/tampering);
- active impersonation/header mutation is never performed automatically;
- local FastAPI + responsive architecture/assumptions Web UI;
- offline synthetic demo, scope checks, plugin inspection, AI-disabled mode and signed-update primitive through SRIC.

- proxy/gateway chain reconstruction, identity transformation graphs and trust-path mutation diff;
- JWT metadata sanitation, header provenance, contradiction detection and direct-origin path comparison;
- declarative Kubernetes/Istio/Envoy configuration import without cluster access and a strict Trust Assertion DSL;
- SRIC 0.3 jobs/SSE, evidence lineage, notebook/search and shared temporal graph primitives;

## Five-minute start

```bash
trustboundary doctor
trustboundary demo --workspace demo
trustboundary map demo
trustboundary assumptions demo
trustboundary web demo
```

Offline lab:

```bash
trustboundary init lab
trustboundary import lab examples/lab/architecture.json
trustboundary map lab
trustboundary assumptions lab
```

## Truth model

A possible trust inconsistency stays `HYPOTHESIS`. It is never treated as exploitation proof. Missing architecture is recorded as a limitation/counter-explanation.

## Safety and privacy

Use only authorized evidence and targets. Non-loopback Web UI binding is refused until authenticated TLS mode is configured. Telemetry/cloud AI/external uploads default to off.

## Documentation

See `docs/` and `ROADMAP.md` for concepts, architecture, threat model, formats, AI/plugins and deferred protocol/cloud adapters.

## License

Apache-2.0.
