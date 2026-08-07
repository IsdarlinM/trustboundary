from fastapi.testclient import TestClient

from trustboundary.api_vnext import create_app


def test_websocket_post_revocation_message_is_hypothesis_only() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/websocket/trust-paths",
        json={
            "observations": [
                {
                    "observation_id": "handshake",
                    "connection_id": "CONN-1",
                    "sequence_index": 0,
                    "stage": "HANDSHAKE",
                    "component_id": "gateway",
                    "identity_artifact_id": "token-1",
                    "subject_hash": "subject-a",
                    "tenant_id": "tenant-a",
                },
                {
                    "observation_id": "auth",
                    "connection_id": "CONN-1",
                    "sequence_index": 1,
                    "stage": "AUTHENTICATION",
                    "component_id": "gateway",
                    "identity_artifact_id": "token-1",
                    "subject_hash": "subject-a",
                    "tenant_id": "tenant-a",
                    "validator": "jwt-filter",
                    "accepted": true,
                    "evidence_ids": ["E-AUTH"]
                },
                {
                    "observation_id": "upgrade",
                    "connection_id": "CONN-1",
                    "sequence_index": 2,
                    "stage": "UPGRADE",
                    "component_id": "gateway",
                    "identity_artifact_id": "token-1",
                    "subject_hash": "subject-a",
                    "tenant_id": "tenant-a",
                    "accepted": true,
                    "evidence_ids": ["E-UPGRADE"]
                },
                {
                    "observation_id": "revoke",
                    "connection_id": "CONN-1",
                    "sequence_index": 3,
                    "stage": "REVOCATION",
                    "component_id": "gateway",
                    "identity_artifact_id": "token-1",
                    "subject_hash": "subject-a",
                    "tenant_id": "tenant-a",
                    "evidence_ids": ["E-REVOKE"]
                },
                {
                    "observation_id": "after",
                    "connection_id": "CONN-1",
                    "sequence_index": 4,
                    "stage": "MESSAGE",
                    "component_id": "api",
                    "identity_artifact_id": "token-1",
                    "subject_hash": "subject-a",
                    "tenant_id": "tenant-a",
                    "accepted": true,
                    "evidence_ids": ["E-AFTER"]
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "HYPOTHESIS"
    assert payload["reports"][0]["messages_after_revocation"] == ["after"]
    assert payload["exploitability_established"] is False
    assert payload["validated_findings_created"] == 0


def test_incomplete_websocket_path_remains_unknown() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/websocket/trust-paths",
        json={
            "observations": [
                {
                    "observation_id": "handshake",
                    "connection_id": "CONN-2",
                    "sequence_index": 0,
                    "stage": "HANDSHAKE",
                    "component_id": "gateway"
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "UNKNOWN"
    assert "authentication observation" in payload["reports"][0]["missing_stages"]
