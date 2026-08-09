# Web/CLI feature parity

TrustBoundary Mapper 0.5.6 mounts the shared SRIC Web Feature Workbench at `/workbench` and retains `/console` as an advanced argv-oriented surface.

The native trust-graph dashboard exposes **All Features** and **Advanced Console** navigation. The Workbench derives its schema from `trustboundary.cli_all`, so every public command and ordered CLI parameter has a structured responsive Web control. `/api/v1/workbench/coverage` reports exact parity.

Execution remains outside an operating-system shell: the fixed `sric.web_console_runner` uses `shell=False`, disabled stdin, CSRF protection, secret redaction, bounded/cancellable jobs and SSE output. Scope/Policy/Rate/Approval and evidence/provenance semantics remain authoritative.

A Web invocation cannot promote `INFERRED`/`HYPOTHESIS` trust inconsistencies to `VALIDATED` exploitability without deterministic evidence and human-controlled validation.

The release tests invoke help for every public command, verify all options/required arguments, compare the complete ordered CLI parameter tree with the Workbench schema and smoke-test native trust-analysis APIs. Destructive actions are gate-tested instead of being executed merely for coverage.
