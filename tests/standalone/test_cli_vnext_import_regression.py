from typer.testing import CliRunner

from trustboundary.cli_all import app


runner = CliRunner()


def test_complete_cli_imports_and_exposes_vnext_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.output
    for command in (
        "import-platform",
        "layer-compare",
        "identity-trace",
        "identity-analyze",
        "routes",
        "jwt-paths",
        "proxy-diff",
        "confusion",
        "path-search",
        "assumption-review",
    ):
        assert command in result.output
