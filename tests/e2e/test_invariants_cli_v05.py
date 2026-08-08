import json
from pathlib import Path

from typer.testing import CliRunner

from trustboundary.cli_all import app

runner = CliRunner()


def test_invariant_evaluate_cli(tmp_path: Path) -> None:
    path = tmp_path / "invariant.json"
    path.write_text(
        json.dumps(
            {
                "invariant": {
                    "invariant_id": "inv-1",
                    "kind": "VERIFIED_IDENTITY",
                    "data_type": "identity",
                },
                "transitions": [
                    {
                        "transition_id": "t1",
                        "source_node_id": "gateway",
                        "target_node_id": "service",
                        "data_type": "identity",
                        "verified": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["invariant-evaluate", str(path)])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["result"]["status"] == "HYPOTHESIS"
    assert payload["validated_findings_created"] == 0
