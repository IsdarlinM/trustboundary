from __future__ import annotations

from enum import StrEnum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from sric.models import ClaimStatus

from .models import Transition


class TrustInvariantKind(StrEnum):
    VERIFIED_IDENTITY = "VERIFIED_IDENTITY"
    STRIP_CLIENT_HEADER = "STRIP_CLIENT_HEADER"
    REQUIRED_TRANSFORMATION = "REQUIRED_TRANSFORMATION"
    PROVENANCE_PRESERVED = "PROVENANCE_PRESERVED"


class TrustInvariant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invariant_id: str
    kind: TrustInvariantKind
    target_node_id: str | None = None
    data_type: str | None = None
    header_name: str | None = None
    required_transformation: str | None = None

    @model_validator(mode="after")
    def required_parameters(self) -> "TrustInvariant":
        if self.kind is TrustInvariantKind.STRIP_CLIENT_HEADER and not self.header_name:
            raise ValueError("STRIP_CLIENT_HEADER requires header_name")
        if self.kind is TrustInvariantKind.REQUIRED_TRANSFORMATION and not self.required_transformation:
            raise ValueError("REQUIRED_TRANSFORMATION requires required_transformation")
        return self


class TrustInvariantResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invariant_id: str
    status: ClaimStatus
    transition_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def automated_results_cannot_validate(self) -> "TrustInvariantResult":
        if self.status is ClaimStatus.VALIDATED:
            raise ValueError("automated trust invariant evaluation cannot create VALIDATED results")
        return self


def _matches(invariant: TrustInvariant, transition: Transition) -> bool:
    if invariant.target_node_id and transition.target_node_id != invariant.target_node_id:
        return False
    if invariant.data_type and transition.data_type.casefold() != invariant.data_type.casefold():
        return False
    if invariant.header_name:
        name = invariant.header_name.casefold()
        if (transition.input_name or "").casefold() != name and (
            transition.output_name or ""
        ).casefold() != name:
            return False
    return True


def evaluate_trust_invariant(
    invariant: TrustInvariant,
    transitions: Sequence[Transition],
) -> TrustInvariantResult:
    """Evaluate an architecture invariant without asserting exploitability."""

    matched = [transition for transition in transitions if _matches(invariant, transition)]
    transition_ids = sorted(transition.transition_id for transition in matched)
    evidence_ids = sorted({value for transition in matched for value in transition.evidence_ids})
    if not matched:
        return TrustInvariantResult(
            invariant_id=invariant.invariant_id,
            status=ClaimStatus.UNKNOWN,
            missing_evidence=["matching transition observation"],
            reasons=["No transition evidence matched the invariant scope."],
        )

    if invariant.kind is TrustInvariantKind.VERIFIED_IDENTITY:
        if any(transition.verified is False for transition in matched):
            return TrustInvariantResult(
                invariant_id=invariant.invariant_id,
                status=ClaimStatus.HYPOTHESIS,
                transition_ids=transition_ids,
                evidence_ids=evidence_ids,
                reasons=["Identity-bearing transition is explicitly modeled as unverified."],
                counter_evidence=[
                    "Verification may occur in code or infrastructure outside the imported evidence."
                ],
            )
        if all(transition.verified is True for transition in matched):
            return TrustInvariantResult(
                invariant_id=invariant.invariant_id,
                status=ClaimStatus.OBSERVED,
                transition_ids=transition_ids,
                evidence_ids=evidence_ids,
                reasons=["All matching transitions contain observed verification evidence."],
            )
        return TrustInvariantResult(
            invariant_id=invariant.invariant_id,
            status=ClaimStatus.UNKNOWN,
            transition_ids=transition_ids,
            evidence_ids=evidence_ids,
            missing_evidence=["verification state"],
            reasons=["At least one matching transition has unknown verification state."],
        )

    if invariant.kind is TrustInvariantKind.STRIP_CLIENT_HEADER:
        preserved_client = [
            transition
            for transition in matched
            if transition.metadata.get("client_supplied") is True
            and transition.metadata.get("stripped") is not True
            and (transition.input_name or "").casefold()
            == (transition.output_name or transition.input_name or "").casefold()
        ]
        stripped = [transition for transition in matched if transition.metadata.get("stripped") is True]
        if preserved_client:
            return TrustInvariantResult(
                invariant_id=invariant.invariant_id,
                status=ClaimStatus.HYPOTHESIS,
                transition_ids=transition_ids,
                evidence_ids=evidence_ids,
                reasons=["A client-supplied identity header is modeled as preserved across the boundary."],
                counter_evidence=["Downstream code may independently reject or replace the header."],
            )
        if stripped and len(stripped) == len(matched):
            return TrustInvariantResult(
                invariant_id=invariant.invariant_id,
                status=ClaimStatus.OBSERVED,
                transition_ids=transition_ids,
                evidence_ids=evidence_ids,
                reasons=["Matching client headers are modeled as stripped at the boundary."],
            )
        return TrustInvariantResult(
            invariant_id=invariant.invariant_id,
            status=ClaimStatus.UNKNOWN,
            transition_ids=transition_ids,
            evidence_ids=evidence_ids,
            missing_evidence=["client origin or strip behavior"],
            reasons=["Header origin/sanitization evidence is incomplete."],
        )

    if invariant.kind is TrustInvariantKind.REQUIRED_TRANSFORMATION:
        expected = invariant.required_transformation
        assert expected is not None
        mismatches = [transition for transition in matched if transition.transformation != expected]
        if mismatches:
            return TrustInvariantResult(
                invariant_id=invariant.invariant_id,
                status=ClaimStatus.HYPOTHESIS,
                transition_ids=transition_ids,
                evidence_ids=evidence_ids,
                reasons=[f"Observed transformation differs from required value: {expected}."],
            )
        return TrustInvariantResult(
            invariant_id=invariant.invariant_id,
            status=ClaimStatus.OBSERVED,
            transition_ids=transition_ids,
            evidence_ids=evidence_ids,
            reasons=[f"All matching transitions use required transformation: {expected}."],
        )

    preserved = [
        transition for transition in matched if transition.metadata.get("provenance_preserved") is True
    ]
    lost = [
        transition for transition in matched if transition.metadata.get("provenance_preserved") is False
    ]
    if lost:
        return TrustInvariantResult(
            invariant_id=invariant.invariant_id,
            status=ClaimStatus.HYPOTHESIS,
            transition_ids=transition_ids,
            evidence_ids=evidence_ids,
            reasons=["Identity provenance is explicitly modeled as not preserved."],
        )
    if len(preserved) == len(matched):
        return TrustInvariantResult(
            invariant_id=invariant.invariant_id,
            status=ClaimStatus.OBSERVED,
            transition_ids=transition_ids,
            evidence_ids=evidence_ids,
            reasons=["Identity provenance is preserved across all matching transitions."],
        )
    return TrustInvariantResult(
        invariant_id=invariant.invariant_id,
        status=ClaimStatus.UNKNOWN,
        transition_ids=transition_ids,
        evidence_ids=evidence_ids,
        missing_evidence=["provenance preservation state"],
        reasons=["Provenance evidence is incomplete."],
    )
