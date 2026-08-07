from fastapi.testclient import TestClient

from trustboundary.api_vnext import create_app


def _base_path_observations() -> list[dict[str, object]]:
    return [
        {
            "observation_id": "handshake",
            "connection_id": "CONN-1",
            "sequence_index": 0,
            "stage": "HANDSHAKE",
            "component_id": "gateway",
            "identity_artifact_id": "token-1",
            "subject_hash": "subject-a",
            "tenant_id": "tenant-a",
            "evidence_ids": ["E-HANDSHAKE"],
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
            "accepted": True,
            "evidence_ids": ["E-AUTH"],
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
            "accepted": True,
            "evidence_ids": ["E-UPGRADE"],
        },
    ]


def test_websocket_post_revocation_message_is_hypothesis_only_with_control() -> None:
    client = TestClient(create_app())
    observations = _base_path_observations()
    observations.extend(
        [
            {
                "observation_id": "before",
                "connection_id": "CONN-1",
                "sequence_index": 3,
                "stage": "MESSAGE",
                "component_id": "api",
                "identity_artifact_id": "token-1",
                "subject_hash": "subject-a",
                "tenant_id": "tenant-a",
                "accepted": True,
                "evidence_ids": ["E-BEFORE"],
            },
            {
                "observation_id": "revoke",
                "connection_id": "CONN-1",
                "sequence_index": 4,
                "stage": "REVOCATION",
                "component_id": "gateway",
                "identity_artifact_id": "token-1",
                "subject_hash": "subject-a",
                "tenant_id": "tenant-a",
                "evidence_ids": ["E-REVOKE"],
            },
            {
                "observation_id": "after",
                "connection_id": "CONN-1",
                "sequence_index": 5,
                "stage": "MESSAGE",
                "component_id": "api",
                "identity_artifact_id": "token-1",
                "subject_hash": "subject-a",
                "tenant_id": "tenant-a",
                "accepted": True,
                "evidence_ids": ["E-AFTER"],
            },
        ]
    )
    response = client.post(
        "/api/v1/analysis/websocket/trust-paths",
        json={"observations": observations},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "HYPOTHESIS"
    assert payload["reports"][0]["messages_before_revocation"] == ["before"]
    assert payload["reports"][0]["messages_after_revocation"] == ["after"]
    assert payload["exploitability_established"] is False
    assert payload["validated_findings_created"] == 0


def test_post_revocation_message_without_precontrol_remains_unknown() -> None:
    client = TestClient(create_app())
    observations = _base_path_observations()
    observations.extend(
        [
            {
                "observation_id": "revoke",
                "connection_id": "CONN-1",
                "sequence_index": 3,
                "stage": "REVOCATION",
                "component_id": "gateway",
                "evidence_ids": ["E-REVOKE"],
            },
            {
                "observation_id": "after",
                "connection_id": "CONN-1",
                "sequence_index": 4,
                "stage": "MESSAGE",
                "component_id": "api",
                "accepted": True,
                "evidence_ids": ["E-AFTER"],
            },
        ]
    )
    response = client.post(
        "/api/v1/analysis/websocket/trust-paths",
        json={"observations": observations},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "UNKNOWN"
    assert "pre-revocation message control" in payload["reports"][0]["missing_stages"]


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
                    "component_id": "gateway",
                    "evidence_ids": ["E-HANDSHAKE"],
                }
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "UNKNOWN"
    assert "authentication observation" in payload["reports"][0]["missing_stages"]


def test_websocket_api_rejects_missing_evidence_without_server_error() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/websocket/trust-paths",
        json={
            "observations": [
                {
                    "observation_id": "handshake",
                    "connection_id": "CONN-3",
                    "sequence_index": 0,
                    "stage": "HANDSHAKE",
                    "component_id": "gateway",
                }
            ]
        },
    )
    assert response.status_code == 422
