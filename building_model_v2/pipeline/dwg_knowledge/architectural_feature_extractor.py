"""Architectural wall extraction from DXF files."""
from __future__ import annotations

from typing import Any

import ezdxf


class ArchitecturalFeatureExtractor:
    """Extract wall entities from DXF documents."""

    def extract_walls(self, document: ezdxf.document.Drawing) -> list[dict[str, Any]]:
        """Extract wall entities from a loaded DXF document."""
        modelspace = document.modelspace()
        walls: list[dict[str, Any]] = []
        wall_index = 0

        for entity in modelspace:
            dxftype = entity.dxftype()
            if dxftype == "LINE":
                points = self._line_points(entity)
            elif dxftype == "LWPOLYLINE":
                points = self._lwpolyline_points(entity)
            elif dxftype == "POLYLINE":
                points = self._polyline_points(entity)
            else:
                continue

            if not self._has_nonzero_length(points):
                continue

            wall_index += 1
            walls.append(
                {
                    "id": f"wall-{wall_index}",
                    "type": dxftype,
                    "layer": str(entity.dxf.layer) if entity.dxf.hasattr("layer") else "",
                    "points": points,
                }
            )

        return walls

    def wall_count(self, document: ezdxf.document.Drawing) -> int:
        """Return the number of extracted wall entities."""
        return len(self.extract_walls(document))

    def _line_points(self, entity: ezdxf.entities.Line) -> list[tuple[float, float]]:
        start = entity.dxf.start
        end = entity.dxf.end
        return [(float(start.x), float(start.y)), (float(end.x), float(end.y))]

    def _lwpolyline_points(self, entity: ezdxf.entities.LWPolyline) -> list[tuple[float, float]]:
        return [(float(x), float(y)) for x, y in entity.get_points("xy")]

    def _polyline_points(self, entity: ezdxf.entities.Polyline) -> list[tuple[float, float]]:
        return [(float(point.x), float(point.y)) for point in entity.points()]

    def _has_nonzero_length(self, points: list[tuple[float, float]]) -> bool:
        if len(points) < 2:
            return False

        total_length = 0.0
        previous = points[0]
        for point in points[1:]:
            dx = point[0] - previous[0]
            dy = point[1] - previous[1]
            total_length += (dx ** 2 + dy ** 2) ** 0.5
            previous = point

        return total_length > 0.0
