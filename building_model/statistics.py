"""Building-level statistics calculation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .models import BuildingModel, BuildingStatistics


class BuildingStatisticsCalculator:
    """Compute aggregate metrics from a building model or module outputs."""

    def calculate(
        self,
        *,
        rooms: Sequence[Mapping[str, Any]],
        walls: Sequence[Mapping[str, Any]],
        doors: Sequence[Mapping[str, Any]],
        windows: Sequence[Mapping[str, Any]],
        adjacency_graph: Sequence[Mapping[str, Any]],
        connectivity_graph: Sequence[Mapping[str, Any]],
        facing_information: Mapping[str, Any] | None,
        zoning: Sequence[Mapping[str, Any]],
        confidence: Sequence[Mapping[str, Any]],
    ) -> BuildingStatistics:
        room_count = len(rooms)
        total_area = sum(_float(room.get("area")) for room in rooms)
        total_perimeter = sum(_float(room.get("perimeter")) for room in rooms)
        confidence_values = [_float(item.get("confidence")) for item in confidence]
        zones = Counter(str(item.get("zone")) for item in zoning if item.get("zone"))

        return BuildingStatistics(
            room_count=room_count,
            wall_count=len(walls),
            door_count=len(doors),
            window_count=len(windows),
            total_room_area=round(total_area, 6),
            average_room_area=round(total_area / room_count, 6) if room_count else 0.0,
            total_room_perimeter=round(total_perimeter, 6),
            adjacency_edge_count=_undirected_edge_count(adjacency_graph, "adjacent_rooms"),
            connectivity_edge_count=_connectivity_edge_count(connectivity_graph),
            front_room_count=len(facing_information.get("front_rooms", ())) if facing_information else 0,
            average_confidence=(
                round(sum(confidence_values) / len(confidence_values), 6)
                if confidence_values
                else 0.0
            ),
            zones=dict(zones),
        )

    def from_model(self, model: BuildingModel) -> BuildingStatistics:
        return self.calculate(
            rooms=model.rooms,
            walls=model.walls,
            doors=model.doors,
            windows=model.windows,
            adjacency_graph=model.adjacency_graph,
            connectivity_graph=model.connectivity_graph,
            facing_information=model.facing_information,
            zoning=model.zoning,
            confidence=model.confidence,
        )


def _float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _undirected_edge_count(records: Sequence[Mapping[str, Any]], key: str) -> int:
    edges: set[tuple[str, str]] = set()
    for record in records:
        room_id = str(record.get("room_id", ""))
        for other_id in record.get(key, ()) or ():
            edges.add(tuple(sorted((room_id, str(other_id)))))
    return len(edges)


def _connectivity_edge_count(records: Sequence[Mapping[str, Any]]) -> int:
    edges: set[tuple[str, str]] = set()
    for record in records:
        room_id = str(record.get("room_id", ""))
        for connection in record.get("connected_rooms", ()) or ():
            edges.add(tuple(sorted((room_id, str(connection.get("room_id", ""))))))
    return len(edges)
