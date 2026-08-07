from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli_vnext import app
from .websocket import WebSocketTrustObservation, analyze_websocket_trust_paths


@app.command("websocket-trust")
def websocket_trust(path: Path) -> None:
    """Analyze sampled WebSocket handshake, identity and revocation trust paths."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(raw, list):
        raise typer.BadParameter("WebSocket trust observations JSON must be a list")
    try:
        observations = [WebSocketTrustObservation.model_validate(item) for item in raw]
        reports = analyze_websocket_trust_paths(observations)
    except (ValidationError, ValueError) as exc:
        typer.echo(f"invalid WebSocket trust input: {exc}", err=True)
        raise typer.Exit(2) from exc
    typer.echo(
        json.dumps(
            [item.model_dump(mode="json") for item in reports],
            indent=2,
            default=str,
        )
    )
