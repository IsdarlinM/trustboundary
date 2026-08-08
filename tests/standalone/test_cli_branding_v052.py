from typer.testing import CliRunner

from sric.cli_style import build_banner
from trustboundary.cli_all import BRAND, app


def test_trustboundary_brand_identity() -> None:
    banner = build_banner(BRAND)
    assert "TrustBoundary Mapper" in banner
    assert "identity flows" in banner
    assert "IsdarlinM :: v0.5.2" in banner


def test_root_help_documents_no_color() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--no-color" in result.stdout
