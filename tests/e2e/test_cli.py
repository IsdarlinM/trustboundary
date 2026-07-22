from typer.testing import CliRunner
from trustboundary.cli import app

r = CliRunner()

def test_help() -> None:
    for args in [["--help"], ["-h"], ["help"], ["map", "--help"]]:
        assert r.invoke(app, args).exit_code == 0
