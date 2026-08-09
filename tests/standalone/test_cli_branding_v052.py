from typer.main import get_command

from sric.cli_style import build_banner
from trustboundary import __version__
from trustboundary.cli_all import BRAND, app


def test_trustboundary_brand_identity() -> None:
    banner = build_banner(BRAND)
    product = banner.index(f"TrustBoundary Mapper :: v{__version__}")
    developer = banner.index("Developer: IsdarlinM")
    description = banner.index("identity flows")
    assert product < developer < description
    assert "IsdarlinM ::" not in banner


def test_no_color_option_is_registered() -> None:
    command = get_command(app)
    assert any("--no-color" in getattr(param, "opts", ()) for param in command.params)
