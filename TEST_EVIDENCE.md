# Test Evidence — trustboundary v0.3.0

Validated 2026-07-22.
- pytest: **20 tests passed**
- compileall: **PASS**
- security scan: **PASS**
- CLI help coverage: **44 registered TrustBoundary command paths** passed `--help`/`-h`
- synthetic/local functional smoke: **PASS**
- wheel build and isolated wheel smoke against validated dependency layer: **PASS**

Ecosystem total: **208 tests**, **263 registered CLI paths**.

Limitations: fresh dependency resolution was blocked by the environment index; Ruff/mypy/pip-audit were unavailable for a fresh local rerun; Windows installers and real-browser E2E were not executed in this Linux runtime. CI retains those gates where available.
