# Local release validation

TrustBoundary Mapper does not depend on GitHub Actions or another hosted CI service.

```bash
python -m pip install -e ../sric-core
python -m pip install -e '.[dev]'
python scripts/release-gate.py
```

The complete local gate runs compilation, Ruff, strict mypy, all pytest suites, project security/evaluation scripts when present, dependency audit, SBOM generation when available, package build, isolated wheel installation and root CLI help checks. Evidence and SHA-256 artifact hashes are written under `build/release-evidence/`.

`--quick` is development-only. A release requires a complete `PASS` report for the exact source commit.
