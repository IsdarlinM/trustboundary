from collections.abc import Iterator

import click
from typer.main import get_command
from typer.testing import CliRunner

from trustboundary.cli_all import app, normalize_help_argv

runner = CliRunner()


def command_paths() -> Iterator[list[str]]:
    root = get_command(app)

    def walk(group: click.Group, prefix: list[str]) -> Iterator[list[str]]:
        for name, command in sorted(group.commands.items()):
            path = [*prefix, name]
            yield path
            if isinstance(command, click.Group):
                yield from walk(command, path)

    if isinstance(root, click.Group):
        yield from walk(root, [])


def test_help_variants_use_complete_entrypoint() -> None:
    for args in (["--help"], ["-h"], ["help"]):
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert "map" in result.output
        assert "websocket-trust" in result.output


def test_every_registered_command_supports_short_and_long_help() -> None:
    paths = list(command_paths())
    assert paths
    for path in paths:
        for flag in ("--help", "-h"):
            result = runner.invoke(app, [*path, flag])
            assert result.exit_code == 0, f"{path} {flag}: {result.output}"
            assert "Traceback" not in result.output


def test_trailing_help_normalization_works_at_every_depth() -> None:
    for path in command_paths():
        argv = ["trustboundary", *path, "help"]
        normalized = normalize_help_argv(argv)
        assert normalized[-1] == "--help"
        assert normalized[:-1] == argv[:-1]
