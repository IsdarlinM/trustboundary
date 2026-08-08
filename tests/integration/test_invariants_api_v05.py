from pathlib import Path

from fastapi.testclient import TestClient

from trustboundary.api_vnext import create_app


def test_invariant_api_never_validates(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    response = client.post(
        "/api/v1/analysis/invariants/evaluate",
        json={
            "invariant": {
                "invariant_id": "inv-1",
                "kind": "VERIFIED_IDENTITY",
                "target_node_id": "service",
                "data_type": "identity",
            },
            "transitions": [
                {
                    "transition_id": "t1",
                    "source_node_id": "gateway",
                    "target_node_id": "service",
                    "data_type": "identity",
                    "verified": False,
                    "evidence_ids": ["ev-1"],
                }
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["status"] == "HYPOTHESIS"
    assert payload["exploitability_established"] is False
    assert payload["validated_findings_created"] == 0
