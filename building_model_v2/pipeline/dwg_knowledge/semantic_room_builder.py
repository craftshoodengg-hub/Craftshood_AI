"""Build semantic room objects from room polygon dictionaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SemanticRoom:
    """Unified semantic representation of a detected room."""

    room_id: str
    room_type: str
    raw_label: str
    polygon: list[Any]
    centroid: tuple[float, float]
    area: float
    perimeter: float
    layer: str
    doors: list[dict[str, Any]] = field(default_factory=list)
    windows: list[dict[str, Any]] = field(default_factory=list)
    door_count: int = 0
    window_count: int = 0
    orientation: str | None = None
    adjacent_rooms: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the semantic room to a plain dictionary."""
        return {
            "room_id": self.room_id,
            "room_type": self.room_type,
            "raw_label": self.raw_label,
            "polygon": list(self.polygon),
            "centroid": self.centroid,
            "area": self.area,
            "perimeter": self.perimeter,
            "layer": self.layer,
            "doors": list(self.doors),
            "windows": list(self.windows),
            "door_count": self.door_count,
            "window_count": self.window_count,
            "orientation": self.orientation,
            "adjacent_rooms": list(self.adjacent_rooms),
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SemanticRoom":
        """Restore a semantic room from a dictionary payload."""
        room_type = str(payload.get("room_type", ""))
        raw_label = str(payload.get("raw_label", room_type))
        polygon = list(payload.get("polygon", []))
        centroid = tuple(payload.get("centroid", (0.0, 0.0)))
        area = float(payload.get("area", 0.0))
        perimeter = float(payload.get("perimeter", 0.0))
        layer = str(payload.get("layer", ""))
        doors = list(payload.get("doors", []))
        windows = list(payload.get("windows", []))
        door_count = int(payload.get("door_count", len(doors)))
        window_count = int(payload.get("window_count", len(windows)))
        orientation = payload.get("orientation")
        adjacent_rooms = list(payload.get("adjacent_rooms", []))
        attributes = dict(payload.get("attributes", {}))

        room_id = str(payload.get("room_id") or cls._build_room_id(room_type, room_type))
        return cls(
            room_id=room_id,
            room_type=room_type,
            raw_label=raw_label,
            polygon=polygon,
            centroid=centroid,
            area=area,
            perimeter=perimeter,
            layer=layer,
            doors=doors,
            windows=windows,
            door_count=door_count,
            window_count=window_count,
            orientation=orientation,
            adjacent_rooms=adjacent_rooms,
            attributes=attributes,
        )

    @staticmethod
    def _build_room_id(room_type: str, raw_label: str) -> str:
        normalized_room_type = "_".join(room_type.lower().split())
        if not normalized_room_type:
            normalized_room_type = "room"
        return f"{normalized_room_type}_1"


class SemanticRoomBuilder:
    """Build semantic room objects from room polygon dictionaries."""

    def build(self, room_polygons: list[dict[str, Any]]) -> list[SemanticRoom]:
        """Build a deterministic list of semantic rooms from room dictionaries."""
        rooms: list[SemanticRoom] = []
        type_counts: dict[str, int] = {}

        for room_payload in room_polygons:
            room_type = str(room_payload.get("room_type", "room"))
            room_type_key = room_type.lower()
            count = type_counts.get(room_type_key, 0) + 1
            type_counts[room_type_key] = count
            room_id = self._build_room_id(room_type, count)

            semantic_room = SemanticRoom(
                room_id=room_id,
                room_type=room_type,
                raw_label=str(room_payload.get("raw_label", room_type)),
                polygon=list(room_payload.get("polygon", [])),
                centroid=tuple(room_payload.get("centroid", (0.0, 0.0))),
                area=float(room_payload.get("area", 0.0)),
                perimeter=float(room_payload.get("perimeter", 0.0)),
                layer=str(room_payload.get("layer", "")),
                doors=list(room_payload.get("doors", [])),
                windows=list(room_payload.get("windows", [])),
                door_count=int(room_payload.get("door_count", len(room_payload.get("doors", [])))),
                window_count=int(room_payload.get("window_count", len(room_payload.get("windows", [])))),
                orientation=None,
                adjacent_rooms=[],
                attributes={},
            )
            rooms.append(semantic_room)

        return rooms

    @staticmethod
    def _build_room_id(room_type: str, count: int) -> str:
        normalized_room_type = "_".join(room_type.lower().split())
        if not normalized_room_type:
            normalized_room_type = "room"
        return f"{normalized_room_type}_{count}"
