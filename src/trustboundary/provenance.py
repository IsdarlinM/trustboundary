from __future__ import annotations

from collections import defaultdict
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus


class IdentityArtifactType(StrEnum):
    JWT = "JWT"
    OPAQUE_TOKEN = "OPAQUE_TOKEN"
    MTLS_IDENTITY = "MTLS_IDENTITY"
    SPIFFE_ID = "SPIFFE_ID"
    SIGNED_HEADER = "SIGNED_HEADER"
    FORWARDED_HEADER = "FORWARDED_HEADER"
    SESSION = "SESSION"
    UNKNOWN = "UNKNOWN"


class ProvenanceStepType(StrEnum):
    ORIGIN = "ORIGIN"
    VALIDATION = "VALIDATION"
    TRANSFORMATION = "TRANSFORMATION"
    TOKEN_EXCHANGE = "TOKEN_EXCHANGE"
    FORWARDING = "FORWARDING"
    CONSUMPTION = "CONSUMPTION"


class IdentityProvenanceStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str
    artifact_id: str
    artifact_type: IdentityArtifactType
    step_type: ProvenanceStepType
    component_id: str
    sequence_index: int = Field(ge=0)
    issuer: str | None = None
    audience_before: str | None = None
    audience_after: str | None = None
    subject_before_hash: str | None = None
    subject_after_hash: str | None = None
    validator: str | None = None
    algorithm: str | None = None
    key_id_hash: str | None = None
    signed_fields: list[str] = Field(default_factory=list)
    trusted_headers: list[str] = Field(default_factory=list)
    transformation: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def step_semantics(self) -> "IdentityProvenanceStep":
        if self.step_type in {
            ProvenanceStepType.VALIDATION,
            ProvenanceStepType.TRANSFORMATION,
            ProvenanceStepType.TOKEN_EXCHANGE,
            ProvenanceStepType.CONSUMPTION,
        } and not self.evidence_ids:
            raise ValueError("evidence-bearing provenance steps require evidence_ids")
        if self.step_type is ProvenanceStepType.VALIDATION and not self.validator:
            raise ValueError("validation steps require validator")
        if (
            self.artifact_type is IdentityArtifactType.SIGNED_HEADER
            and not self.signed_fields
        ):
            raise ValueError("signed-header provenance requires signed_fields")
        if (
            self.step_type is ProvenanceStepType.TOKEN_EXCHANGE
            and not self.audience_after
        ):
            raise ValueError("token exchange requires audience_after")
        return self


class IdentityProvenanceReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    status: ClaimStatus
    step_ids: list[str]
    origin_components: list[str] = Field(default_factory=list)
    validators: list[str] = Field(default_factory=list)
    consumers: list[str] = Field(default_factory=list)
    transformations: list[str] = Field(default_factory=list)
    audience_path: list[str] = Field(default_factory=list)
    missing_stages: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def analyze_identity_provenance(
    steps: Sequence[IdentityProvenanceStep],
) -> list[IdentityProvenanceReport]:
    grouped: dict[str, list[IdentityProvenanceStep]] = defaultdict(list)
    for step in steps:
        grouped[step.artifact_id].append(step)

    output: list[IdentityProvenanceReport] = []
    for artifact_id in sorted(grouped):
        values = sorted(
            grouped[artifact_id],
            key=lambda item: (item.sequence_index, item.step_id),
        )
        missing: list[str] = []
        contradictions: list[str] = []
        origins = [
            item.component_id
            for item in values
            if item.step_type is ProvenanceStepType.ORIGIN
        ]
        validators = [
            str(item.validator)
            for item in values
            if item.step_type is ProvenanceStepType.VALIDATION and item.validator
        ]
        consumers = [
            item.component_id
            for item in values
            if item.step_type is ProvenanceStepType.CONSUMPTION
        ]
        transformations = [
            str(item.transformation)
            for item in values
            if item.transformation
        ]
        if not origins:
            missing.append("identity origin")
        if not validators:
            missing.append("identity validator")
        if not consumers:
            missing.append("identity consumer")

        indices = [item.sequence_index for item in values]
        if len(indices) != len(set(indices)):
            contradictions.append(
                "Multiple provenance steps share a sequence index; ordering is ambiguous."
            )

        audience_path: list[str] = []
        current_audience: str | None = None
        current_subject: str | None = None
        for item in values:
            if item.audience_before:
                if current_audience and item.audience_before != current_audience:
                    contradictions.append(
                        f"Audience discontinuity before {item.step_id}: "
                        f"expected {current_audience}, observed {item.audience_before}."
                    )
                current_audience = item.audience_before
                if not audience_path or audience_path[-1] != current_audience:
                    audience_path.append(current_audience)
            if item.audience_after:
                current_audience = item.audience_after
                if not audience_path or audience_path[-1] != current_audience:
                    audience_path.append(current_audience)
            if item.subject_before_hash:
                if current_subject and item.subject_before_hash != current_subject:
                    contradictions.append(
                        f"Subject provenance discontinuity before {item.step_id}."
                    )
                current_subject = item.subject_before_hash
            if item.subject_after_hash:
                current_subject = item.subject_after_hash

        signed_header_steps = [
            item
            for item in values
            if item.artifact_type is IdentityArtifactType.SIGNED_HEADER
        ]
        for item in signed_header_steps:
            if not item.algorithm:
                missing.append(f"signature algorithm for {item.step_id}")
            if not item.validator and item.step_type is not ProvenanceStepType.ORIGIN:
                missing.append(f"signature validator for {item.step_id}")

        evidence_ids = sorted(
            {evidence for item in values for evidence in item.evidence_ids}
        )
        counter_ids = sorted(
            {
                evidence
                for item in values
                for evidence in item.counter_evidence_ids
            }
        )
        if missing or contradictions:
            status = ClaimStatus.UNKNOWN
        else:
            status = ClaimStatus.OBSERVED

        output.append(
            IdentityProvenanceReport(
                artifact_id=artifact_id,
                status=status,
                step_ids=[item.step_id for item in values],
                origin_components=sorted(set(origins)),
                validators=sorted(set(validators)),
                consumers=sorted(set(consumers)),
                transformations=transformations,
                audience_path=audience_path,
                missing_stages=sorted(set(missing)),
                contradictions=sorted(set(contradictions)),
                evidence_ids=evidence_ids,
                counter_evidence_ids=counter_ids,
                limitations=[
                    "Complete provenance describes the sampled identity path; it does not establish authorization correctness or exploitability.",
                    "Token contents and key material are represented by hashes or metadata and must not be stored as secrets in the graph.",
                ],
            )
        )
    return output
