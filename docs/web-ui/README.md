# Web UI

The local Web UI reads the same workspace model as the CLI/API. It exposes architecture, trust assumptions, identity transformations, contradictions, search and job events backed by real APIs; it does not expose synthetic actions or bypass policy. Non-loopback deployment must be protected by authenticated TLS before production use; v0.2 remains local-first by default. The UI uses same-origin API calls and a restrictive CSP.
