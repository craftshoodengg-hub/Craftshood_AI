"""Room confidence scoring.

The scorer combines geometric quality and graph/context availability into a
weighted confidence value from 0.0 to 1.0. It consumes already-computed room
polygon, adjacency, connectivity, facing, and metadata inputs; it does not
perform detection.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from shapely.geometry import Polygon


class QualityLabel(StrEnum):
    """Human-friendly confidence quality labels."""

    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"


@dataclass(frozen=True, slots=True)
class RoomMetadata:
    """Metadata associated with a room polygon."""

    room_id: str
    room_name: str | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ConfidenceWeights:
    """Weighted scoring configuration.

    Default weights sum to 1.0.
    """

    closed_polygon: float = 0.20
    valid_geometry: float = 0.25
    known_room_name: float = 0.15
    adjacency_available: float = 0.15
    connectivity_available: float = 0.15
    facing_available: float = 0.10

    def normalized(self) -> dict[str, float]:
        weights = {
            "closed_polygon": self.closed_polygon,
            "valid_geometry": self.valid_geometry,
            "known_room_name": self.known_room_name,
            "adjacency_available": self.adjacency_available,
            "connectivity_available": self.connectivity_available,
            "facing_available": self.facing_available,
        }
        if any(value < 0 for value in weights.values()):
            raise ValueError("Confidence weights must be non-negative")

        total = sum(weights.values())
        if total <= 0:
            raise ValueError("At least one confidence weight must be greater than zero")
        return {key: value / total for key, value in weights.items()}


@dataclass(frozen=True, slots=True)
class ConfidenceConfig:
    """Confidence scoring configuration."""

    weights: ConfidenceWeights = field(default_factory=ConfidenceWeights)
    score_precision: int = 2
    known_room_names: frozenset[str] = frozenset(
        {
            "Living",
            "M.bed room",
            "Bed room",
            "Kitchen",
            "Dining",
            "Toilet",
            "Sitout",
            "Portico",
        }
    )


@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    """Confidence scoring result for one room."""

    room_id: str
    confidence: float
    quality: QualityLabel
    breakdown: Mapping[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "confidence": self.confidence,
            "quality": self.quality.value,
            "breakdown": dict(self.breakdown),
        }


class ConfidenceScorer:
    """Calculate weighted confidence scores for detected rooms."""

    def __init__(self, config: ConfidenceConfig | None = None) -> None:
        self.config = config or ConfidenceConfig()
        if self.config.score_precision < 0:
            raise ValueError("score_precision must be non-negative")
        self._weights = self.config.weights.normalized()

    def score(
        self,
        polygon: Polygon,
        adjacency_information: Mapping[str, Any] | None,
        connectivity_information: Mapping[str, Any] | None,
        facing_information: Mapping[str, Any] | None,
        metadata: RoomMetadata | Mapping[str, Any],
    ) -> dict[str, Any]:
        """Return a JSON-friendly confidence result."""

        return self.score_result(
            polygon,
            adjacency_information,
            connectivity_information,
            facing_information,
            metadata,
        ).to_dict()

    def score_result(
        self,
        polygon: Polygon,
        adjacency_information: Mapping[str, Any] | None,
        connectivity_information: Mapping[str, Any] | None,
        facing_information: Mapping[str, Any] | None,
        metadata: RoomMetadata | Mapping[str, Any],
    ) -> ConfidenceResult:
        """Return a typed confidence result."""

        room_metadata = _coerce_metadata(metadata)
        breakdown = {
            "closed_polygon": _is_closed_polygon(polygon),
            "valid_geometry": bool(polygon.is_valid and not polygon.is_empty),
            "known_room_name": self._is_known_room_name(room_metadata.room_name),
            "adjacency_available": _adjacency_available(adjacency_information),
            "connectivity_available": _connectivity_available(connectivity_information),
            "facing_available": _facing_available(facing_information, room_metadata.room_id),
        }
        confidence = sum(
            self._weights[key] for key, passed in breakdown.items() if passed
        )
        rounded_confidence = round(float(confidence), self.config.score_precision)
        return ConfidenceResult(
            room_id=room_metadata.room_id,
            confidence=rounded_confidence,
            quality=quality_for_score(rounded_confidence),
            breakdown=breakdown,
        )

    def _is_known_room_name(self, room_name: str | None) -> bool:
        if room_name is None:
            return False
        normalized = " ".join(str(room_name).split()).strip().lower()
        return normalized in {name.lower() for name in self.config.known_room_names}


def calculate_confidence(
    polygon: Polygon,
    adjacency_information: Mapping[str, Any] | None,
    connectivity_information: Mapping[str, Any] | None,
    facing_information: Mapping[str, Any] | None,
    metadata: RoomMetadata | Mapping[str, Any],
    *,
    config: ConfidenceConfig | None = None,
) -> dict[str, Any]:
    """Convenience wrapper around :class:`ConfidenceScorer`."""

    return ConfidenceScorer(config).score(
        polygon,
        adjacency_information,
        connectivity_information,
        facing_information,
        metadata,
    )


def quality_for_score(score: float) -> QualityLabel:
    """Return a human-readable quality label for a 0.0-1.0 score."""

    if score >= 0.90:
        return QualityLabel.EXCELLENT
    if score >= 0.75:
        return QualityLabel.GOOD
    if score >= 0.50:
        return QualityLabel.FAIR
    return QualityLabel.POOR


def _coerce_metadata(metadata: RoomMetadata | Mapping[str, Any]) -> RoomMetadata:
    if isinstance(metadata, RoomMetadata):
        if not metadata.room_id:
            raise ValueError("room_id cannot be empty")
        return metadata

    room_id = str(metadata.get("room_id", "")).strip()
    if not room_id:
        raise ValueError("room_id cannot be empty")
    room_name = metadata.get("room_name", metadata.get("name"))
    return RoomMetadata(
        room_id=room_id,
        room_name=None if room_name is None else str(room_name),
        extra={key: value for key, value in metadata.items() if key not in {"room_id", "room_name", "name"}},
    )


def _is_closed_polygon(polygon: Polygon) -> bool:
    if polygon.is_empty:
        return False
    coordinates = list(polygon.exterior.coords)
    if len(coordinates) < 4:
        return False
    return coordinates[0] == coordinates[-1]


def _adjacency_available(adjacency_information: Mapping[str, Any] | None) -> bool:
    if not adjacency_information:
        return False
    adjacent_rooms = adjacency_information.get("adjacent_rooms")
    shared_boundary_length = adjacency_information.get("shared_boundary_length")
    return bool(adjacent_rooms) or bool(shared_boundary_length)


def _connectivity_available(connectivity_information: Mapping[str, Any] | None) -> bool:
    if not connectivity_information:
        return False
    return bool(connectivity_information.get("connected_rooms"))


def _facing_available(
    facing_information: Mapping[str, Any] | None,
    room_id: str,
) -> bool:
    if not facing_information:
        return False

    road_side = facing_information.get("road_side")
    front_wall_id = facing_information.get("front_wall_id")
    front_rooms = facing_information.get("front_rooms", ())
    if not road_side or road_side == "Unknown" or not front_wall_id:
        return False
    return room_id in set(str(room) for room in front_rooms)
