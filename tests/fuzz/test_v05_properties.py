from __future__ import annotations

from hypothesis import given, strategies as st
from sric.models import ClaimStatus

from trustboundary.invariants import TrustInvariant, TrustInvariantKind, evaluate_trust_invariant
from trustboundary.models import Transition


@given(st.one_of(st.none(), st.booleans()))
def test_generated_identity_invariant_never_validates(verified: bool | None) -> None:
    result = evaluate_trust_invariant(
        TrustInvariant(
            invariant_id="generated",
            kind=TrustInvariantKind.VERIFIED_IDENTITY,
            data_type="identity",
        ),
        [
            Transition(
                transition_id="transition-generated",
                source_node_id="gateway",
                target_node_id="service",
                data_type="identity",
                verified=verified,
                evidence_ids=["ev-generated"],
            )
        ],
    )
    assert result.status in {
        ClaimStatus.OBSERVED,
        ClaimStatus.HYPOTHESIS,
        ClaimStatus.UNKNOWN,
    }
    assert result.status is not ClaimStatus.VALIDATED


@given(st.booleans(), st.booleans())
def test_generated_client_header_analysis_never_validates(
    client_supplied: bool,
    stripped: bool,
) -> None:
    result = evaluate_trust_invariant(
        TrustInvariant(
            invariant_id="header-generated",
            kind=TrustInvariantKind.STRIP_CLIENT_HEADER,
            header_name="X-User-Id",
        ),
        [
            Transition(
                transition_id="transition-generated",
                source_node_id="internet",
                target_node_id="gateway",
                data_type="header",
                input_name="X-User-Id",
                output_name="X-User-Id",
                metadata={"client_supplied": client_supplied, "stripped": stripped},
            )
        ],
    )
    assert result.status is not ClaimStatus.VALIDATED
