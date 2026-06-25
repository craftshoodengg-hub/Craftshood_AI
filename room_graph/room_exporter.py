"""JSON export for room graph results."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from loguru import logger

from geometry_engine import LogicalWall

from .boundary_finder import BoundaryFinderConfig, RoomCenter
from .graph_builder import RoomGraphBuilder, RoomGraphResult
from .polygon_builder import PolygonBuilderConfig


class RoomExporter:
    """Build and export room boundary graph JSON."""

    def __init__(
        self,
        *,
        builder: RoomGraphBuilder | None = None,
        boundary_config: BoundaryFinderConfig | None = None,
        polygon_config: PolygonBuilderConfig | None = None,
    ) -> None:
        self.builder = builder or RoomGraphBuilder(
            boundary_config=boundary_config,
            polygon_config=polygon_config,
        )

    def build_room(
        self,
        room_name: str,
        center: RoomCenter,
        logical_walls: Iterable[LogicalWall],
    ) -> RoomGraphResult:
        return self.builder.build_room(room_name, center, logical_walls)

    def export_room_json(
        self,
        room_name: str,
        center: RoomCenter,
        logical_walls: Iterable[LogicalWall],
        output_path: str | Path | None = None,
        *,
        indent: int = 2,
    ) -> str:
        """Export one room graph result as JSON and optionally write it to disk."""

        result = self.build_room(room_name, center, logical_walls)
        json_text = json.dumps(result.to_dict(), indent=indent, sort_keys=True)
        if output_path is not None:
            target = Path(output_path).expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json_text, encoding="utf-8")
            logger.info("Wrote room graph JSON to {}", target)
        return json_text
