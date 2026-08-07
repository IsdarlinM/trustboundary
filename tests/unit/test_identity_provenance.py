import pytest

from sric.models import ClaimStatus
from trustboundary.provenance import (
    IdentityArtifactType,
    IdentityProvenanceStep,
    ProvenanceStepType,
    analyze_identity_provenance,
)


def step(
    step_id: str,
    step_type: ProvenanceStepType,
    index: int,
    *,
    component: str,
    evidence: list[str] | None = None,
    validator: str | None = None,
    audience_before: str | None = None,
    audience_after: str | None = None,
    subject_before: str | None = None,
    subject_after: str | None = None,
) -> IdentityProvenanceStep:
    return IdentityProvenanceStep(
        step_id=step_id,
        artifact_id="token-1",
        artifact_type=IdentityArtifactType.JWT,
        step_type=step_type,
        component_id=component,
        sequence_index=index,
        validator=validator,
        audience_before=audience_before,
        audience_after=audience_after,
        subject_before_hash=subject_before,
        subject_after_hash=subject_after,
        evidence_ids=evidence or [],
    )


def complete_path() -> list[IdentityProvenanceStep]:
    return [
        step(
            "origin",
            ProvenanceStepType.ORIGIN,
            0,
            component="issuer",
            audience_after="gateway",
            subject_after="subject-a",
        ),
        step(
            "validate",
            ProvenanceStepType.VALIDATION,
            1,
            component="gateway",
            validator="gateway-jwt-filter",
            audience_before="gateway",
            audience_after="gateway",
            subject_before="subject-a",
            subject_after="subject-a",
            evidence=["E-V"],
        ),
        step(
            "exchange",
            ProvenanceStepType.TOKEN_EXCHANGE,
            2,
            component="gateway",
            audience_before="gateway",
            audience_after="api",
            subject_before="subject-a",
            subject_after="subject-a",
            evidence=["E-X"],
        ),
        step(
            "consume",
            ProvenanceStepType.CONSUMPTION,
            3,
            component="api",
            audience_before="api",
            subject_before="subject-a",
            evidence=["E-C"],
        ),
    ]


def test_complete_sampled_path_is_observed_with_limitations() -> None:
    report = analyze_identity_provenance(complete_path())[0]

    assert report.status is ClaimStatus.OBSERVED
    assert report.audience_path == ["gateway", "api"]
    assert report.validators == ["gateway-jwt-filter"]
    assert "does not establish authorization" in report.limitations[0]


def test_missing_validator_remains_unknown() -> None:
    values = [
        item
        for item in complete_path()
        if item.step_type is not ProvenanceStepType.VALIDATION
    ]

    report = analyze_identity_provenance(values)[0]

    assert report.status is ClaimStatus.UNKNOWN
    assert "identity validator" in report.missing_stages


def test_audience_discontinuity_is_reported() -> None:
    values = complete_path()
    values[-1].audience_before = "different-api"

    report = analyze_identity_provenance(values)[0]

    assert report.status is ClaimStatus.UNKNOWN
    assert any("Audience discontinuity" in item for item in report.contradictions)


def test_subject_discontinuity_is_reported() -> None:
    values = complete_path()
    values[-1].subject_before_hash = "different-subject"

    report = analyze_identity_provenance(values)[0]

    assert report.status is ClaimStatus.UNKNOWN
    assert any("Subject provenance discontinuity" in item for item in report.contradictions)


def test_duplicate_sequence_index_is_ambiguous() -> None:
    values = complete_path()
    values[-1].sequence_index = 2

    report = analyze_identity_provenance(values)[0]

    assert report.status is ClaimStatus.UNKNOWN
    assert any("ordering is ambiguous" in item for item in report.contradictions)


def test_validation_step_requires_validator_and_evidence() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        step(
            "invalid",
            ProvenanceStepType.VALIDATION,
            0,
            component="gateway",
            validator="validator",
        )
    with pytest.raises(ValueError, match="require validator"):
        step(
            "invalid",
            ProvenanceStepType.VALIDATION,
            0,
            component="gateway",
            evidence=["E-1"],
        )


def test_signed_header_requires_signed_field_metadata() -> None:
    with pytest.raises(ValueError, match="requires signed_fields"):
        IdentityProvenanceStep(
            step_id="signed",
            artifact_id="header-1",
            artifact_type=IdentityArtifactType.SIGNED_HEADER,
            step_type=ProvenanceStepType.ORIGIN,
            component_id="gateway",
            sequence_index=0,
        )


def test_token_exchange_requires_resulting_audience() -> None:
    with pytest.raises(ValueError, match="requires audience_after"):
        step(
            "exchange",
            ProvenanceStepType.TOKEN_EXCHANGE,
            0,
            component="gateway",
            evidence=["E-X"],
        )
