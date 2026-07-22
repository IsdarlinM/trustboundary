# CLI Reference — trustboundary v0.2.0

All public commands support `COMMAND --help` and `COMMAND -h`; `trustboundary COMMAND help` is normalized to the same command help path.

## Root commands

- `version` — print the installed version.
- `doctor` — check Python, SRIC 0.3 integration, AI-disabled defaults and plugin registry.
- `init` — initialize a workspace.
- `workspace` — create/list/show/archive isolated workspaces; archive requires explicit confirmation.
- `config` — show/explain secure configuration values and their source.
- `observe` — add an observed architecture node.
- `transition` — add an observed/modelled trust transition with optional evidence.
- `assertion` — add an explicit trust assertion.
- `import` — import architecture JSON or passive HAR metadata; no replay is generated.
- `import-config` — import supplied Kubernetes/Istio/Envoy configuration without contacting a cluster.
- `assertion-dsl` — parse the strict, auditable Trust Assertion DSL.
- `map` — show the current architecture/trust graph.
- `identities` — show identity-bearing flows.
- `assumptions` — produce explainable `HYPOTHESIS` candidates with evidence/counter-evidence.
- `paths` — enumerate modeled paths between two nodes.
- `compare` — compare incoming trust transitions for two nodes.
- `validate` — mark a candidate validated only with `--confirm` and explicit evidence; no impersonation/tampering is executed automatically.
- `timeline` — show observed transition chronology.
- `proxy-chains` — reconstruct candidate proxy/gateway chains from supplied evidence.
- `transformations` — show identity/header/token transformations and provenance state.
- `trust-diff` — compare two modeled trust paths without active bypass attempts.
- `jwt` — sanitize a supplied decoded JWT claims JSON document to non-secret identity/routing metadata.
- `header-provenance` — explain where a trust/identity header was introduced or transformed.
- `contradictions` — identify contradictions between explicit assertions and modeled/observed facts.
- `origin-paths` — compare gateway-mediated and alternate modeled paths without probing targets.
- `export` — export the workspace graph as JSON.
- `report` — create an evidence-aware Markdown report.
- `demo` — create an offline synthetic demonstration workspace.
- `web` — run the local Web UI; non-loopback binding is refused by default.
- `evidence` — store a local artifact in SRIC content-addressed evidence storage.
- `ai` — show AI mode; cloud AI remains disabled by default.
- `plugins` — inspect SRIC plugin manifests without auto-executing plugin code.
- `scope` — evaluate a target through SRIC Scope Engine without sending a request.
- `query` — search the shared temporal graph.
- `notebook` — list/add research notes and saved queries.
- `evidence-lineage` — explain evidence lineage for a derived artifact.
- `jobs` — list/inspect/cancel persistent SRIC jobs.
- `update` — check/install only signed wheel releases; never blind `git pull`.
- `help` — root/top-level help dispatcher.

Use `trustboundary <command> --help` for authoritative arguments and options for the installed version.
