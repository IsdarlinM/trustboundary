# CLI presentation

TrustBoundary Mapper 0.5.7 uses the shared Sentinel Forge CLI presentation contract from SRIC Core.

Interactive console sessions show a subdued green ASCII banner ordered as `TrustBoundary Mapper :: v0.5.7`, `Developer: IsdarlinM`, then the concise purpose statement. The banner is written to interactive stderr, keeping stdout suitable for JSON, graph data, redirection, and automation.

Use `trustboundary --no-color COMMAND` to disable ANSI/Rich colors. The installed console entrypoint also normalizes `trustboundary COMMAND --no-color`. The standard `NO_COLOR` environment variable is honored.

The public help contract includes `trustboundary --help`, `trustboundary -h`, `trustboundary help`, `trustboundary COMMAND --help`, `trustboundary COMMAND -h`, and `trustboundary COMMAND help`. The release regression suite walks every public command and compares its ordered CLI parameters with the Web Feature Workbench schema.

Typer/Rich command and help presentation is colorized by default. `--no-color` changes presentation only; it does not alter trust paths, evidence, invariants, provenance, update verification, Web Feature Workbench/Command Console behavior, or API responses.
