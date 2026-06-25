"""JSON import/export for building models."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from shapely.geometry import mapping as shapely_mapping
from shapely.geometry.base import BaseGeometry

from .models import BuildingModel, BuildingStatistics


class BuildingModelSerializer:
    """Serialize and deserialize :class:`BuildingModel` instances."""

    def to_dict(self, model: BuildingModel) -> dict[str, Any]:
        return _json_safe(model.to_dict())

    def to_json(self, model: BuildingModel, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(model), indent=indent, sort_keys=True)

    def write_json(self, model: BuildingModel, output_path: str | Path, *, indent: int = 2) -> str:
        json_text = self.to_json(model, indent=indent)
        target = Path(output_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json_text, encoding="utf-8")
        return json_text

    def from_dict(self, payload: Mapping[str, Any]) -> BuildingModel:
        statistics_payload = dict(payload.get("statistics", {}) or {})
        return BuildingModel(
            metadata=dict(payload.get("metadata", {}) or {}),
            plot=payload.get("plot"),
            walls=tuple(payload.get("walls", ()) or ()),
            doors=tuple(payload.get("doors", ()) or ()),
            windows=tuple(payload.get("windows", ()) or ()),
            rooms=tuple(payload.get("rooms", ()) or ()),
            adjacency_graph=tuple(payload.get("adjacency_graph", ()) or ()),
            connectivity_graph=tuple(payload.get("connectivity_graph", ()) or ()),
            facing_information=payload.get("facing_information"),
            zoning=tuple(payload.get("zoning", ()) or ()),
            confidence=tuple(payload.get("confidence", ()) or ()),
            statistics=BuildingStatistics(**statistics_payload),
        )

    def from_json(self, json_text: str) -> BuildingModel:
        return self.from_dict(json.loads(json_text))

    def read_json(self, input_path: str | Path) -> BuildingModel:
        source = Path(input_path).expanduser().resolve()
        return self.from_json(source.read_text(encoding="utf-8"))


def _json_safe(value: Any) -> Any:
    if isinstance(value, BaseGeometry):
        return shapely_mapping(value)
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_safe(item) for item in value]
    return value
