import pytest

from sric.models import ClaimStatus
from trustboundary.layers import (
    ArchitectureLayer,
    TrustDrift,
    TrustLayerObservation,
    analyze_forwarding_headers,
    compare_trust_layers,
)


def observation(
    observation_id: str,
    layer: ArchitectureLayer,
    *,
    validator: str = "gateway",
    headers: list[str] | None = None,
    evidence: list[str] | None = None,
) -> TrustLayerObservation:
    return TrustLayerObservation(
        observation_id=observation_id,
        edge_id="edge-1",
        layer=layer,
        source_component="edge",
        destination_component="api",
        identity_source="jwt",
        validator=validator,
        consumer="api",
        token_type="JWT",
        issuer="https://issuer.example",
        audience="api",
        trusted_headers=headers or ["x-user-id"],
        source_id=f"source-{layer.lower()}",
        evidence_ids=evidence or [],
    )


def complete(*, observed_validator: str = "gateway") -> list[TrustLayerObservation]:
    return [
        observation("declared", ArchitectureLayer.DECLARED, evidence=["E-D"]),
        observation("configured", ArchitectureLayer.CONFIGURED, evidence=["E-C"]),
        observation(
            "observed",
            ArchitectureLayer.OBSERVED,
            validator=observed_validator,
            evidence=["E-O"],
        ),
    ]


def test_observed_trust_path_requires_evidence() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        observation("observed", ArchitectureLayer.OBSERVED)


def test_missing_layer_remains_unknown() -> None:
    result = compare_trust_layers(
        [
            observation("declared", ArchitectureLayer.DECLARED, evidence=["E-D"]),
            observation("observed", ArchitectureLayer.OBSERVED, evidence=["E-O"]),
        ]
    )[0]

    assert result.status is ClaimStatus.UNKNOWN
    assert ArchitectureLayer.CONFIGURED in result.missing_layers
    assert result.skeptic_verdict == "UNKNOWN"


def test_runtime_drift_is_hypothesis_not_exploitation() -> None:
    result = compare_trust_layers(complete(observed_validator="application"))[0]

    assert result.status is ClaimStatus.HYPOTHESIS
    assert TrustDrift.RUNTIME_DRIFT in result.drifts
    assert TrustDrift.IDENTITY_TRANSFORMATION_DRIFT in result.drifts
    assert result.alternative_explanations
    assert result.confidence <= 0.79


def test_consistent_sample_has_explicit_limitation() -> None:
    result = compare_trust_layers(complete())[0]

    assert result.status is ClaimStatus.OBSERVED
    assert result.drifts == [TrustDrift.CONSISTENT_SAMPLE]
    assert "does not prove every route" in result.limitations[0]


def test_conflicting_observed_paths_become_unknown() -> None:
    values = complete()
    values.append(
        observation(
            "observed-conflict",
            ArchitectureLayer.OBSERVED,
            validator="application",
            evidence=["E-O2"],
        )
    )

    result = compare_trust_layers(values)[0]

    assert result.status is ClaimStatus.UNKNOWN
    assert ArchitectureLayer.OBSERVED in result.missing_layers


def test_header_names_are_case_insensitive_but_values_are_preserved() -> None:
    result = analyze_forwarding_headers(
        [("X-Forwarded-For", "198.51.100.2"), ("x-forwarded-for", "10.0.0.5")]
    )

    assert result.duplicate_names == ["x-forwarded-for"]
    assert result.conflicting_names == ["x-forwarded-for"]
    assert result.forwarding_chain == ["198.51.100.2", "10.0.0.5"]
    assert "must not be collapsed" in result.limitations[0]


def test_forwarded_and_x_forwarded_for_precedence_is_unknown() -> None:
    result = analyze_forwarding_headers(
        [("Forwarded", "for=198.51.100.2"), ("X-Forwarded-For", "198.51.100.2")]
    )

    assert any("precedence" in limitation for limitation in result.limitations)
