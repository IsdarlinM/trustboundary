from typer.testing import CliRunner
from trustboundary.cli import app


def test_validate_requires_human_confirmation() -> None:
    r = CliRunner().invoke(app, ["validate", "missing", "TBC-1"])
    assert r.exit_code != 0
