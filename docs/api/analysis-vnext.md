# Analysis API

Run the extended local API on loopback:

```bash
python -m uvicorn trustboundary.api_vnext:create_app --factory --host 127.0.0.1 --port 8766
```

Additional endpoints:

```text
POST /api/v1/analysis/layers/compare
POST /api/v1/analysis/headers/analyze
POST /api/v1/analysis/architecture/import
POST /api/v1/analysis/provenance/analyze
```

Imported configurations and provenance records are parsed as untrusted data and never executed. Drift, header ambiguity and provenance completeness do not establish exploitability or authorization impact.
