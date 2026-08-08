from __future__ import annotations

from sric.models import ClaimStatus
from trustboundary.invariants import (
    TrustInvariant,
    TrustInvariantKind,
    evaluate_trust_invariant,
)
from trustboundary.models import Transition


def test_unverified_identity_produces_hypothesis_not_validation() -> None:
    invariant = TrustInvariant(
        invariant_id="inv-1",
        kind=TrustInvariantKind.VERIFIED_IDENTITY,
        target_node_id="service",
        data_type="identity",
    )
    result = evaluate_trust_invariant(
        invariant,
        [
            Transition(
                transition_id="t1",
                source_node_id="gateway",
                target_node_id="service",
                data_type="identity",
                verified=False,
                evidence_ids=["ev-1"],
            )
        ],
    )
    assert result.status is ClaimStatus.HYPOTHESIS
    assert result.evidence_ids == ["ev-1"]


def test_verified_identity_is_observed() -> None:
    invariant = TrustInvariant(
        invariant_id="inv-2",
        kind=TrustInvariantKind.VERIFIED_IDENTITY,
        data_type="jwt",
    )
    result = evaluate_trust_invariant(
        invariant,
        [
            Transition(
                transition_id="t1",
                source_node_id="gateway",
                target_node_id="service",
                data_type="jwt",
                verified=True,
            )
        ],
    )
    assert result.status is ClaimStatus.OBSERVED


def test_client_header_preservation_is_only_hypothesis() -> None:
    invariant = TrustInvariant(
        invariant_id="inv-3",
        kind=TrustInvariantKind.STRIP_CLIENT_HEADER,
        header_name="X-User-Id",
    )
    result = evaluate_trust_invariant(
        invariant,
        [
            Transition(
                transition_id="t1",
                source_node_id="internet",
                target_node_id="gateway",
                data_type="header",
                input_name="X-User-Id",
                output_name="X-User-Id",
                metadata={"client_supplied": True, "stripped": False},
            )
        ],
    )
    assert result.status is ClaimStatus.HYPOTHESIS
