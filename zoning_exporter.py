"""JSON export helpers for zoning results."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from zoning import ZoningClassifier
from zoning_rules import ZoningRulesConfig


class ZoningExporter:
    """Classify rooms and export zoning results as JSON."""

    def __init__(
        self,
        *,
        classifier: ZoningClassifier | None = None,
        config: ZoningRulesConfig | None = None,
    ) -> None:
        self.classifier = classifier or ZoningClassifier(config)

    def export_room(
        self,
        room_id: str,
        room_name: str | None,
        output_path: str | Path | None = None,
        *,
        indent: int = 2,
    ) -> str:
        """Export one room zoning result as JSON."""

        return self._dump_json(
            self.classifier.classify(room_id, room_name),
            output_path,
            indent=indent,
        )

    def export_rooms(
        self,
        rooms: Iterable[Mapping[str, Any]],
        output_path: str | Path | None = None,
        *,
        indent: int = 2,
    ) -> str:
        """Export many room zoning results as JSON."""

        payload = [
            self.classifier.classify(
                str(room.get("room_id", "")),
                None if room.get("room_name") is None else str(room.get("room_name")),
            )
            for room in rooms
        ]
        return self._dump_json(payload, output_path, indent=indent)

    def _dump_json(
        self,
        payload: Any,
        output_path: str | Path | None,
        *,
        indent: int,
    ) -> str:
        json_text = json.dumps(payload, indent=indent, sort_keys=True)
        if output_path is not None:
            target = Path(output_path).expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json_text, encoding="utf-8")
        return json_text
