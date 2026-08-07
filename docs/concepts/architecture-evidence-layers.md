# Architecture evidence layers

TrustBoundary compares three distinct representations:

- `DECLARED`: diagrams, design documents and intended trust assumptions.
- `CONFIGURED`: imported gateway, proxy, service-mesh, cloud or workload configuration.
- `OBSERVED`: evidence-bearing runtime identity flow.

Declared/configured differences are configuration drift hypotheses. Configured/observed differences are runtime drift hypotheses. Declared/observed differences are identity-transformation drift hypotheses. Missing or contradictory layer data produces `UNKNOWN`.

A drift does not establish reachability, identity acceptance, authorization impact or exploitability. Those properties require separate evidence and safe validation.

Forwarding headers are treated as ordered observations. Header-name case is normalized, but duplicate values, conflicting values and coexistence between standards are preserved. Trusted proxy count, first/last-hop selection and append/replace semantics must come from configuration or runtime evidence.
