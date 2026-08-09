from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from typer.testing import CliRunner

import trustboundary.sric_bootstrap as bootstrap
from trustboundary.api_all import _mount_degraded_workbench
from trustboundary.cli_all import app, normalize_help_argv
from sric.web_console import build_command_catalog
from sric.web_workbench import build_feature_catalog, feature_contract


def _runtime(version: str, *, compatible: bool, missing: tuple[str, ...] = ()) -> bootstrap.SRICRuntimeStatus:
    return bootstrap.SRICRuntimeStatus(version, compatible, missing, (() if compatible else ("incompatible",)))


def test_stale_core_and_missing_workbench_are_detected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap.importlib.metadata, "version", lambda _name: "0.5.5")
    monkeypatch.setattr(bootstrap, "_find_module", lambda _name: False)
    result = bootstrap.status()
    assert result.compatible is False
    assert "sric.web_workbench" in result.missing_modules


def test_bridge_then_normal_update_and_same_version_force(monkeypatch: pytest.MonkeyPatch) -> None:
    updates: list[dict[str, object]] = []
    fake = SimpleNamespace(perform_product_update=lambda **kwargs: updates.append(kwargs))
    states = iter([_runtime("0.5.5", compatible=False), _runtime("0.5.7", compatible=True)])
    bridged: list[bool] = []
    monkeypatch.setattr(bootstrap, "status", lambda: next(states))
    monkeypatch.setattr(bootstrap, "_upgrade_055_to_056", lambda: bridged.append(True))
    monkeypatch.setattr(bootstrap, "_updater", lambda: fake)
    monkeypatch.setattr(bootstrap, "_require_updater_api", lambda *_args: None)
    monkeypatch.setattr(bootstrap.importlib, "invalidate_caches", lambda: None)
    bootstrap.ensure_for_official_update()
    assert bridged == [True]
    assert updates[0]["current_version"] == "0.5.6"
    assert updates[0]["force"] is False

    updates.clear()
    states = iter([_runtime("0.5.7", compatible=False, missing=("sric.web_workbench",)), _runtime("0.5.7", compatible=True)])
    monkeypatch.setattr(bootstrap, "status", lambda: next(states))
    bootstrap.ensure_for_official_update()
    assert updates[0]["force"] is True


def test_degraded_workbench_is_503_not_global_failure() -> None:
    degraded = FastAPI()
    _mount_degraded_workbench(degraded, "missing sric.web_workbench")
    client = TestClient(degraded)
    assert client.get("/workbench").status_code == 503
    assert client.get("/api/v1/workbench/coverage").json()["complete"] is False


def test_every_trustboundary_command_and_param_is_web_represented_and_helpable() -> None:
    cli = build_command_catalog("trustboundary.cli_all")
    web = build_feature_catalog("trustboundary.cli_all")
    assert feature_contract("trustboundary.cli_all")["complete"] is True
    cli_by_path = {item["path"]: item for item in cli}
    web_by_path = {item["path"]: item for item in web}
    assert set(cli_by_path) == set(web_by_path)
    runner = CliRunner()
    for args in (["--help"], ["-h"], ["help"]):
        assert runner.invoke(app, args).exit_code == 0
    for path, command in cli_by_path.items():
        args = path.split()
        assert runner.invoke(app, [*args, "--help"]).exit_code == 0, path
        assert runner.invoke(app, [*args, "-h"]).exit_code == 0, path
        assert normalize_help_argv(["trustboundary", *args, "help"])[-1] == "--help"
        assert [p["name"] for p in command["params"]] == [p["name"] for p in web_by_path[path]["params"]]
