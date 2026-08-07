from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.calibration import ConfidenceSignal, score_confidence, skeptic_review
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ArchitectureLayer(StrEnum):
    DECLARED = "DECLARED"
    CONFIGURED = "CONFIGURED"
    OBSERVED = "OBSERVED"


class TrustDrift(StrEnum):
    CONFIGURATION_DRIFT = "CONFIGURATION_DRIFT"
    RUNTIME_DRIFT = "RUNTIME_DRIFT"
    IDENTITY_TRANSFORMATION_DRIFT = "IDENTITY_TRANSFORMATION_DRIFT"
    HEADER_AMBIGUITY = "HEADER_AMBIGUITY"
    CONSISTENT_SAMPLE = "CONSISTENT_SAMPLE"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"


class HeaderAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    normalized: dict[str, list[str]]
    duplicate_names: list[str] = Field(default_factory=list)
    conflicting_names: list[str] = Field(default_factory=list)
    forwarding_chain: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def analyze_forwarding_headers(headers: Sequence[tuple[str, str]]) -> HeaderAnalysis:
    """Normalize header names without silently resolving duplicate ambiguity."""

    normalized: dict[str, list[str]] = defaultdict(list)
    for raw_name, raw_value in headers:
        name = raw_name.strip().lower()
        if not name:
            continue
        normalized[name].append(raw_value.strip())

    duplicate = sorted(name for name, values in normalized.items() if len(values) > 1)
    conflicting = sorted(
        name for name, values in normalized.items() if len({value for value in values}) > 1
    )
    forwarding_chain: list[str] = []
    for value in normalized.get("x-forwarded-for", []):
        forwarding_chain.extend(part.strip() for part in value.split(",") if part.strip())

    limitations: list[str] = []
    if "forwarded" in normalized and "x-forwarded-for" in normalized:
        limitations.append(
            "Forwarded and X-Forwarded-For coexist; precedence must be established from configuration or runtime evidence."
        )
    if conflicting:
        limitations.append(
            "Conflicting duplicate headers are preserved and must not be collapsed into a trusted identity."
        )
    if forwarding_chain:
        limitations.append(
            "The forwarding chain is observational; trusted proxy count and append/replace semantics remain required."
        )

    return HeaderAnalysis(
        normalized=dict(normalized),
        duplicate_names=duplicate,
        conflicting_names=conflicting,
        forwarding_chain=forwarding_chain,
        limitations=limitations,
    )


class TrustLayerObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: str
    edge_id: str
    layer: ArchitectureLayer
    source_component: str
    destination_component: str
    identity_source: str
    validator: str | None = None
    consumer: str | None = None
    token_type: str | None = None
    issuer: str | None = None
    audience: str | None = None
    trusted_headers: list[str] = Field(default_factory=list)
    transformation: str | None = None
    source_id: str
    source_group: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def observed_requires_evidence(self) -> "TrustLayerObservation":
        if self.layer is ArchitectureLayer.OBSERVED and not self.evidence_ids:
            raise ValueError("OBSERVED trust paths require evidence_ids")
        return self

    def fingerprint(self) -> tuple[object, ...]:
        return (
            self.source_component,
            self.destination_component,
            self.identity_source,
            self.validator,
            self.consumer,
            self.token_type,
            self.issuer,
            self.audience,
            tuple(sorted(name.lower() for name in self.trusted_headers)),
            self.transformation,
        )


class TrustLayerComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edge_id: str
    status: ClaimStatus
    drifts: list[TrustDrift] = Field(default_factory=list)
    missing_layers: list[ArchitectureLayer] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    skeptic_verdict: str
    alternative_explanations: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def _unique_fingerprint(
    items: Sequence[TrustLayerObservation], layer: ArchitectureLayer
) -> tuple[object, ...] | None:
    values = {item.fingerprint() for item in items if item.layer is layer}
    return next(iter(values)) if len(values) == 1 else None


def compare_trust_layers(
    observations: Sequence[TrustLayerObservation],
) -> list[TrustLayerComparison]:
    """Compare declared, configured and observed trust paths without claiming exploitability."""

    grouped: dict[str, list[TrustLayerObservation]] = defaultdict(list)
    for item in observations:
        grouped[item.edge_id].append(item)

    output: list[TrustLayerComparison] = []
    for edge_id in sorted(grouped):
        items = grouped[edge_id]
        values = {
            layer: _unique_fingerprint(items, layer) for layer in ArchitectureLayer
        }
        missing = [layer for layer, value in values.items() if value is None]
        drifts: list[TrustDrift] = []
        alternatives: list[str] = []
        limitations: list[str] = []

        if missing:
            status = ClaimStatus.UNKNOWN
            drifts.append(TrustDrift.INCOMPLETE_EVIDENCE)
            limitations.append(
                "Missing or contradictory architecture layers prevent a complete trust comparison."
            )
        else:
            declared = values[ArchitectureLayer.DECLARED]
            configured = values[ArchitectureLayer.CONFIGURED]
            observed = values[ArchitectureLayer.OBSERVED]
            if declared != configured:
                drifts.append(TrustDrift.CONFIGURATION_DRIFT)
                alternatives.append(
                    "The deployed configuration may intentionally differ from architecture documentation."
                )
            if configured != observed:
                drifts.append(TrustDrift.RUNTIME_DRIFT)
                alternatives.extend(
                    [
                        "The observation may have traversed a different gateway, route or deployment version.",
                        "A service mesh or intermediary may transform identity outside the imported configuration.",
                    ]
                )
            if declared != observed:
                drifts.append(TrustDrift.IDENTITY_TRANSFORMATION_DRIFT)
            if drifts:
                status = ClaimStatus.HYPOTHESIS
            else:
                drifts.append(TrustDrift.CONSISTENT_SAMPLE)
                status = ClaimStatus.OBSERVED
                limitations.append(
                    "Agreement for the sampled path does not prove every route or deployment enforces the same trust assumptions."
                )

        evidence_ids = sorted({value for item in items for value in item.evidence_ids})
        counter_ids = sorted(
            {value for item in items for value in item.counter_evidence_ids}
        )
        signals = [
            ConfidenceSignal(
                signal=f"trust-layer:{item.layer.lower()}",
                contribution=0.18 if item.layer is ArchitectureLayer.OBSERVED else 0.1,
                reason=f"{item.layer} trust path is available",
                source_id=item.source_id,
                source_group=item.source_group,
                evidence_ids=item.evidence_ids,
                observed_at=item.observed_at,
                direct_observation=item.layer is ArchitectureLayer.OBSERVED,
                source_quality=0.9 if item.layer is ArchitectureLayer.OBSERVED else 0.7,
                specificity=0.9,
                temporal_half_life_days=30 if item.layer is ArchitectureLayer.OBSERVED else 180,
            )
            for item in items
        ]
        breakdown = score_confidence(signals, base_confidence=0.05, maximum=0.79)
        review = skeptic_review(
            breakdown,
            alternative_explanations=alternatives,
            counter_evidence_ids=counter_ids,
            missing_required_evidence=[layer.value for layer in missing],
        )
        maximum = 0.49 if status is ClaimStatus.UNKNOWN else 0.79
        if status is ClaimStatus.OBSERVED:
            maximum = 0.69
        output.append(
            TrustLayerComparison(
                edge_id=edge_id,
                status=status,
                drifts=drifts,
                missing_layers=missing,
                observation_ids=sorted(item.observation_id for item in items),
                evidence_ids=evidence_ids,
                counter_evidence_ids=counter_ids,
                confidence=round(min(review.adjusted_confidence, maximum), 6),
                skeptic_verdict=review.verdict.value,
                alternative_explanations=sorted(set(alternatives)),
                limitations=limitations,
            )
        )
    return output
