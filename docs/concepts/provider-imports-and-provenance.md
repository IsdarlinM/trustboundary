# Provider imports and identity provenance

TrustBoundary imports provider configuration as untrusted, import-only architecture evidence.

Initial normalizers cover NGINX, Envoy, Istio/Kubernetes Gateway resources and AWS ALB exports. They validate top-level shapes, report unknown fields and extract bounded listener, route, upstream, trusted-header and identity-validator metadata. Embedded commands, templates and external references are never executed.

Imported configuration belongs to the `DECLARED` or `CONFIGURED` layer. It never proves runtime behavior.

## Identity provenance

`IdentityProvenanceStep` models origin, validation, transformation, token exchange, forwarding and consumption for JWT, opaque tokens, mTLS/SPIFFE identities, signed headers, forwarded headers and sessions.

The analyzer reports:

- origin, validators and consumers;
- audience transitions;
- subject-hash continuity;
- signed fields and signature metadata;
- missing stages;
- ordering, audience and subject contradictions;
- evidence and counter-evidence.

A complete sampled path is `OBSERVED`; missing or contradictory provenance remains `UNKNOWN`. Neither state establishes authorization correctness or exploitability.

CLI examples:

```bash
trustboundary architecture-import config.json --provider envoy --source-id export-1
trustboundary provenance-analyze provenance.json
trustboundary headers-analyze headers.json
trustboundary layer-compare layers.json
```
