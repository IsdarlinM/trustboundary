from __future__ import annotations
import json
from pathlib import Path
from typing import Any, cast


class JsonStore:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()
        if not (self.workspace / "workspace.json").is_file():
            raise FileNotFoundError("workspace.json not found")
        self.path = self.workspace / "trustboundary.json"
        if not self.path.exists():
            self.save({"schema_version": "0.1", "nodes": [], "transitions": [], "assertions": [], "candidates": []})

    def load(self) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.path.read_text(encoding="utf-8")))

    def save(self, data: dict[str, Any]) -> None:
        t = self.path.with_suffix(".tmp")
        t.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        t.replace(self.path)
