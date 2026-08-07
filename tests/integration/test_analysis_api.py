from fastapi.testclient import TestClient

from trustboundary.api_vnext import create_app


def test_header_api_preserves_duplicate_conflicts() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/headers/analyze",
        json={
            "headers": [
                ["X-Forwarded-For", "198.51.100.10"],
                ["x-forwarded-for", "10.0.0.5"],
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["analysis"]["conflicting_names"] == ["x-forwarded-for"]
    assert payload["trusted_identity_selected"] is False


def test_architecture_import_api_never_executes_content() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/architecture/import",
        json={
            "provider": "NGINX",
            "source_id": "export-1",
            "data": {
                "servers": [],
                "embedded_instruction": "execute external command",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["executed"] is False
    assert payload["runtime_behavior_proved"] is False
    assert payload["report"]["unknown_fields"] == ["embedded_instruction"]


def test_incomplete_provenance_does_not_prove_authorization() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/analysis/provenance/analyze",
        json={
            "steps": [
                {
                    "step_id": "origin",
                    "artifact_id": "token-1",
                    "artifact_type": "JWT",
                    "step_type": "ORIGIN",
                    "component_id": "issuer",
                    "sequence_index": 0,
                }
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reports"][0]["status"] == "UNKNOWN"
    assert payload["authorization_correctness_proved"] is False
    assert payload["exploitability_established"] is False
