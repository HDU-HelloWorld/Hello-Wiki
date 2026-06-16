import json
from pathlib import Path
from typing import Any, cast


class JsonFileStore:
    def __init__(self, base_path: str) -> None:
        self._base = Path(base_path)
        self._base.mkdir(parents=True, exist_ok=True)

    def read_json(self, relative_path: str) -> dict[str, Any]:
        target = self._base / relative_path
        if not target.exists():
            return {}
        parsed = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(parsed, dict):
            return cast(dict[str, Any], parsed)
        return {}

    def write_json(self, relative_path: str, payload: dict[str, Any]) -> None:
        target = self._base / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
