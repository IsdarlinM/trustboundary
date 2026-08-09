from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from sric.capabilities import discover_capabilities
from sric.web_console import WebConsoleConfig, mount_web_console
from sric.web_workbench import mount_feature_workbench

from . import __version__
from .api_vnext import create_app as create_base_app


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)

    @app.get("/api/v1/capabilities", tags=["standalone"])
    async def capabilities() -> dict[str, object]:
        return discover_capabilities(current_product="trustboundary").model_dump(mode="json")

    config = WebConsoleConfig(
        product="trustboundary",
        display_name="TrustBoundary Mapper",
        cli_module="trustboundary.cli_all",
        version=__version__,
    )
    manager = mount_web_console(app, config)
    mount_feature_workbench(app, config, manager)
    return app
