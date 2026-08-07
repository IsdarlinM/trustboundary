from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WebSocketTrustStage(StrEnum):
    HANDSHAKE = "HANDSHAKE"
    AUTHENTICATION = "AUTHENTICATION"
    UPGRADE = "UPGRADE"
    MESSAGE = "MESSAGE"
    REAUTHENTICATION = "REAUTHENTICATION"
    REVOCATION = "REVOCATION"
    CLOSE = "CLOSE"


class WebSocketTrustObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str
    connection_id: str
    sequence_index: int = Field(ge=0)
    stage: WebSocketTrustStage
    component_id: str
    identity_artifact_id: str | None = None
    subject_hash: str | None = None
    tenant_id: str | None = None
    audience: str | None = None
    validator: str | None = None
    accepted: bool | None = None
    message_type: str | None = None
    observed_at: datetime = Field(default_factory=utcnow)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def trust_observations_require_evidence(self) -> "WebSocketTrustObservation":
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        if not self.evidence_ids:
            raise ValueError("WebSocket trust observations require evidence_ids")
        if self.stage is WebSocketTrustStage.AUTHENTICATION and not self.validator:
            raise ValueError("authentication observations require a validator")
        return self


class WebSocketTrustPath(BaseModel):
    model_config = ConfigDict(extra="forbid")

    connection_id: str
    status: ClaimStatus
    stages: list[WebSocketTrustStage]
    components: list[str]
    identity_artifact_ids: list[str]
    validators: list[str]
    messages_before_revocation: list[str] = Field(default_factory=list)
    messages_after_revocation: list[str] = Field(default_factory=list)
    missing_stages: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def analyze_websocket_trust_paths(
    observations: Sequence[WebSocketTrustObservation],
) -> list[WebSocketTrustPath]:
    grouped: dict[str, list[WebSocketTrustObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.connection_id].append(observation)

    output: list[WebSocketTrustPath] = []
    for connection_id in sorted(grouped):
        values = sorted(
            grouped[connection_id],
            key=lambda item: (item.sequence_index, item.observed_at, item.observation_id),
        )
        stages = [item.stage for item in values]
        missing: list[str] = []
        contradictions: list[str] = []
        if WebSocketTrustStage.HANDSHAKE not in stages:
            missing.append("handshake observation")
        if WebSocketTrustStage.AUTHENTICATION not in stages:
            missing.append("authentication observation")
        if WebSocketTrustStage.UPGRADE not in stages:
            missing.append("upgrade observation")

        indices = [item.sequence_index for item in values]
        if len(indices) != len(set(indices)):
            contradictions.append("Multiple observations share a sequence index.")

        accepted_auth = [
            item
            for item in values
            if item.stage is WebSocketTrustStage.AUTHENTICATION
            and item.accepted is True
        ]
        rejected_auth = [
            item
            for item in values
            if item.stage is WebSocketTrustStage.AUTHENTICATION
            and item.accepted is False
        ]
        if accepted_auth and rejected_auth:
            contradictions.append(
                "The same connection has accepted and rejected authentication observations."
            )

        revocation_indices = [
            item.sequence_index
            for item in values
            if item.stage is WebSocketTrustStage.REVOCATION
        ]
        messages_before_revocation: list[str] = []
        messages_after_revocation: list[str] = []
        if revocation_indices:
            first_revocation = min(revocation_indices)
            messages_before_revocation = [
                item.observation_id
                for item in values
                if item.stage is WebSocketTrustStage.MESSAGE
                and item.sequence_index < first_revocation
                and item.accepted is not False
            ]
            messages_after_revocation = [
                item.observation_id
                for item in values
                if item.stage is WebSocketTrustStage.MESSAGE
                and item.sequence_index > first_revocation
                and item.accepted is not False
            ]
            if messages_after_revocation and not messages_before_revocation:
                missing.append("pre-revocation message control")

        current_subject: str | None = None
        current_tenant: str | None = None
        for item in values:
            if item.subject_hash:
                if (
                    current_subject
                    and item.subject_hash != current_subject
                    and item.stage
                    not in {
                        WebSocketTrustStage.REAUTHENTICATION,
                        WebSocketTrustStage.AUTHENTICATION,
                    }
                ):
                    contradictions.append(
                        f"Subject changed at {item.observation_id} without an authentication transition."
                    )
                current_subject = item.subject_hash
            if item.tenant_id:
                if (
                    current_tenant
                    and item.tenant_id != current_tenant
                    and item.stage
                    not in {
                        WebSocketTrustStage.REAUTHENTICATION,
                        WebSocketTrustStage.AUTHENTICATION,
                    }
                ):
                    contradictions.append(
                        f"Tenant changed at {item.observation_id} without an authentication transition."
                    )
                current_tenant = item.tenant_id

        if missing or contradictions:
            status = ClaimStatus.UNKNOWN
        elif messages_after_revocation:
            status = ClaimStatus.HYPOTHESIS
        else:
            status = ClaimStatus.OBSERVED

        output.append(
            WebSocketTrustPath(
                connection_id=connection_id,
                status=status,
                stages=stages,
                components=sorted({item.component_id for item in values}),
                identity_artifact_ids=sorted(
                    {
                        str(item.identity_artifact_id)
                        for item in values
                        if item.identity_artifact_id
                    }
                ),
                validators=sorted(
                    {str(item.validator) for item in values if item.validator}
                ),
                messages_before_revocation=messages_before_revocation,
                messages_after_revocation=messages_after_revocation,
                missing_stages=sorted(set(missing)),
                contradictions=sorted(set(contradictions)),
                evidence_ids=sorted(
                    {evidence for item in values for evidence in item.evidence_ids}
                ),
                counter_evidence_ids=sorted(
                    {
                        evidence
                        for item in values
                        for evidence in item.counter_evidence_ids
                    }
                ),
                limitations=[
                    "A sampled WebSocket trust path does not prove every connection follows the same route.",
                    "Messages after revocation are a hypothesis only with a pre-revocation control; timing, buffering, reauthentication and reconnect controls still require evaluation.",
                ],
            )
        )
    return output
