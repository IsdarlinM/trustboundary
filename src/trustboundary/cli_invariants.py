from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError

from .cli_vnext import app
from .invariants import TrustInvariant, evaluate_trust_invariant
from .models import Transition


@app.command("invariant-evaluate")
def invariant_evaluate(
    path: Path = typer.Argument(..., exists=True, dir_okay=False),
) -> None:
    """Evaluate one trust invariant against supplied transition evidence."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("input must be a JSON object")
        invariant = TrustInvariant.model_validate(payload.get("invariant"))
        raw_transitions = payload.get("transitions", [])
        if not isinstance(raw_transitions, list):
            raise ValueError("transitions must be a list")
        transitions = [Transition.model_validate(item) for item in raw_transitions]
        result = evaluate_trust_invariant(invariant, transitions)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
        typer.echo(f"trust invariant evaluation failed: {exc}", err=True)
        raise typer.Exit(2) from exc

    typer.echo(
        json.dumps(
            {
                "result": result.model_dump(mode="json"),
                "exploitability_established": False,
                "validated_findings_created": 0,
            },
            indent=2,
        )
    )
