from datetime import datetime

import pytest

from sric.models import ClaimStatus
from trustboundary.websocket import (
    WebSocketTrustObservation,
    WebSocketTrustStage,
    analyze_websocket_trust_paths,
)


def observation(
    observation_id: str,
    stage: WebSocketTrustStage,
    index: int,
    *,
    accepted: bool | None = None,
    validator: str | None = None,
    subject: str = "subject-a",
    tenant: str = "tenant-a",
) -> WebSocketTrustObservation:
    return WebSocketTrustObservation(
        observation_id=observation_id,
        connection_id="CONN-1",
        sequence_index=index,
        stage=stage,
        component_id="gateway",
        identity_artifact_id="token-1",
        subject_hash=subject,
        tenant_id=tenant,
        validator=validator,
        accepted=accepted,
        evidence_ids=[f"E-{observation_id}"],
    )


def complete_path() -> list[WebSocketTrustObservation]:
    return [
        observation("handshake", WebSocketTrustStage.HANDSHAKE, 0),
        observation(
            "auth",
            WebSocketTrustStage.AUTHENTICATION,
            1,
            accepted=True,
            validator="jwt-filter",
        ),
        observation("upgrade", WebSocketTrustStage.UPGRADE, 2, accepted=True),
        observation("message", WebSocketTrustStage.MESSAGE, 3, accepted=True),
        observation("close", WebSocketTrustStage.CLOSE, 4),
    ]


def test_complete_sampled_path_is_observed_only() -> None:
    report = analyze_websocket_trust_paths(complete_path())[0]
    assert report.status is ClaimStatus.OBSERVED
    assert report.validators == ["jwt-filter"]
    assert "does not prove every connection" in report.limitations[0]


def test_missing_authentication_remains_unknown() -> None:
    values = [
        item
        for item in complete_path()
        if item.stage is not WebSocketTrustStage.AUTHENTICATION
    ]
    report = analyze_websocket_trust_paths(values)[0]
    assert report.status is ClaimStatus.UNKNOWN
    assert "authentication observation" in report.missing_stages


def test_message_after_revocation_is_hypothesis_with_precontrol() -> None:
    values = complete_path()[:4]
    values.extend(
        [
            observation("revoke", WebSocketTrustStage.REVOCATION, 4),
            observation("after", WebSocketTrustStage.MESSAGE, 5, accepted=True),
        ]
    )
    report = analyze_websocket_trust_paths(values)[0]
    assert report.status is ClaimStatus.HYPOTHESIS
    assert report.messages_before_revocation == ["message"]
    assert report.messages_after_revocation == ["after"]


def test_post_revocation_message_without_precontrol_remains_unknown() -> None:
    values = complete_path()[:3]
    values.extend(
        [
            observation("revoke", WebSocketTrustStage.REVOCATION, 3),
            observation("after", WebSocketTrustStage.MESSAGE, 4, accepted=True),
        ]
    )
    report = analyze_websocket_trust_paths(values)[0]
    assert report.status is ClaimStatus.UNKNOWN
    assert "pre-revocation message control" in report.missing_stages


def test_subject_change_without_reauthentication_is_unknown() -> None:
    values = complete_path()
    values[3].subject_hash = "subject-b"
    report = analyze_websocket_trust_paths(values)[0]
    assert report.status is ClaimStatus.UNKNOWN
    assert any("Subject changed" in item for item in report.contradictions)


def test_every_observation_requires_evidence_and_auth_requires_validator() -> None:
    with pytest.raises(ValueError, match="require evidence_ids"):
        WebSocketTrustObservation(
            observation_id="invalid",
            connection_id="CONN-1",
            sequence_index=0,
            stage=WebSocketTrustStage.HANDSHAKE,
            component_id="gateway",
        )
    with pytest.raises(ValueError, match="require a validator"):
        WebSocketTrustObservation(
            observation_id="invalid",
            connection_id="CONN-1",
            sequence_index=0,
            stage=WebSocketTrustStage.AUTHENTICATION,
            component_id="gateway",
            evidence_ids=["E-1"],
        )


def test_naive_observed_at_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        WebSocketTrustObservation(
            observation_id="invalid-time",
            connection_id="CONN-1",
            sequence_index=0,
            stage=WebSocketTrustStage.HANDSHAKE,
            component_id="gateway",
            observed_at=datetime(2026, 1, 1),
            evidence_ids=["E-1"],
        )
