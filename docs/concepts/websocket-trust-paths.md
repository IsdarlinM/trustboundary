# WebSocket trust paths

TrustBoundary 0.3.1 models sampled WebSocket trust transitions across handshake, authentication, upgrade, messages, reauthentication, revocation and close.

The analyzer preserves component, identity artifact, subject hash, tenant, validator, audience and evidence metadata. It reports:

- missing handshake/authentication/upgrade stages;
- duplicate ordering;
- accepted/rejected authentication contradictions;
- subject or tenant changes without an authentication transition;
- messages observed after revocation.

Incomplete or contradictory paths remain `UNKNOWN`. Messages after revocation are `HYPOTHESIS` until buffering, timing, reconnect and reauthentication controls are evaluated. A sampled path never proves that all connections use the same route or that exploitation is possible.

CLI:

```bash
trustboundary websocket-trust websocket-observations.json
```

Loopback API:

```text
POST /api/v1/analysis/websocket/trust-paths
```
