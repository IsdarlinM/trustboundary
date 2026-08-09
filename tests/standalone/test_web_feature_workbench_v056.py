from __future__ import annotations

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from sric.web_console import build_command_catalog
from sric.web_workbench import build_feature_catalog
from trustboundary.api_all import create_app
from trustboundary.cli_all import app

runner = CliRunner()


def test_every_public_cli_command_and_argument_is_represented_in_workbench() -> None:
    cli = {item["path"]: item for item in build_command_catalog("trustboundary.cli_all")}
    web = {item["path"]: item for item in build_feature_catalog("trustboundary.cli_all")}
    assert set(cli) == set(web)
    assert cli
    for path, command in cli.items():
        assert [item["name"] for item in command["params"]] == [
            item["name"] for item in web[path]["params"]
        ]
        assert web[path]["classification"] == command["classification"]
        assert web[path]["approval_required"] == command["approval_required"]


def test_every_public_cli_command_help_exposes_options_and_required_arguments() -> None:
    catalog = build_command_catalog("trustboundary.cli_all")
    assert runner.invoke(app, ["--help"]).exit_code == 0
    for command in catalog:
        result = runner.invoke(app, command["path"].split() + ["--help"])
        assert result.exit_code == 0, f"{command['path']}\n{result.output}"
        normalized = result.output.lower().replace("_", "-")
        for param in command["params"]:
            if param["kind"] == "option":
                for opt in param["opts"]:
                    assert opt in result.output
            elif param["required"]:
                assert param["name"].lower().replace("_", "-") in normalized


def test_workbench_and_native_trust_features(tmp_path) -> None:
    client = TestClient(create_app(tmp_path))
    assert client.get("/workbench").status_code == 200
    payload = client.get("/api/v1/workbench/catalog").json()
    assert payload["contract"]["complete"] is True
    assert payload["execution"]["shell"] is False
    assert payload["execution"]["arbitrary_executable"] is False
    assert {item["path"] for item in payload["features"]} == {
        item["path"] for item in build_command_catalog("trustboundary.cli_all")
    }
    for route in ("/api/graph", "/api/assumptions", "/api/proxy-chains", "/api/transformations", "/api/contradictions", "/api/origin-paths"):
        response = client.get(route)
        assert response.status_code == 200, route
