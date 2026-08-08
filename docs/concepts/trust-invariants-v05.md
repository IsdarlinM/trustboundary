# Trust Invariants in TrustBoundary 0.5

Trust invariants express architecture expectations that can be compared with modeled or observed transitions without claiming exploitability.

Built-in invariant kinds cover verified identity, client-supplied header stripping, required transformations and identity-provenance preservation.

## Result semantics

Automated evaluation returns only:

- `OBSERVED` when matching evidence supports the invariant;
- `HYPOTHESIS` when modeled/observed evidence conflicts with it;
- `UNKNOWN` when required transition, verification, sanitization or provenance evidence is missing.

Invariant evaluation cannot create a `VALIDATED` result. Validation requires evidence-bearing controlled testing through SRIC policy gates.

## Counter-evidence

A conflict result includes plausible counter-explanations where appropriate, such as downstream verification that is not represented in imported architecture evidence. The goal is to expose trust assumptions for investigation rather than convert incomplete diagrams into findings.
