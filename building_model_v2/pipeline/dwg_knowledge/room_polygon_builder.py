"""Build room polygons from DWG wall geometry and room labels."""
from __future__ import annotations

from typing import Any

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polygonize

from .room_label_detector import RoomLabelDetector


class RoomPolygonBuilder:
    """Build room polygons from DXF wall entities and room labels."""

    @staticmethod
    def build(document: Any) -> list[dict[str, Any]]:
        """Return room dictionaries for each label that falls inside a detected polygon."""
        labels = RoomLabelDetector.detect(document)
        wall_segments = []

        for entity in document.modelspace():
            wall_segments.extend(_entity_to_segments(entity))

        if not wall_segments:
            return []

        line_strings = [LineString(segment) for segment in wall_segments if len(segment) == 2]
        if not line_strings:
            return []

        polygons = []
        for geometry in polygonize(line_strings):
            if _is_room_polygon(geometry):
                polygons.append(geometry)

        if not polygons:
            return []

        results: list[dict[str, Any]] = []
        for label in labels:
            position = label.get("position", (0.0, 0.0))
            point = Point(position)
            matched_polygon = None
            for polygon in polygons:
                if polygon.covers(point):
                    matched_polygon = polygon
                    break

            if matched_polygon is None:
                continue

            exterior = list(matched_polygon.exterior.coords)
            if len(exterior) >= 2:
                exterior = exterior[:-1]

            centroid = matched_polygon.centroid
            results.append(
                {
                    "room_type": label.get("room_type", ""),
                    "raw_label": label.get("raw_label", ""),
                    "polygon": exterior,
                    "centroid": (float(centroid.x), float(centroid.y)),
                    "area": float(matched_polygon.area),
                    "perimeter": float(matched_polygon.length),
                    "layer": label.get("layer", ""),
                }
            )

        return results


def _is_room_polygon(geometry: Polygon) -> bool:
    if geometry.geom_type != "Polygon":
        return False
    if geometry.is_empty or not geometry.is_valid:
        return False
    if geometry.area <= 0:
        return False

    exterior = geometry.exterior
    if exterior is None:
        return False

    coordinates = list(exterior.coords)
    if len(coordinates) < 5:
        return False

    return True


def _entity_to_segments(entity: Any) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    entity_type = entity.dxftype()

    if entity_type == "LINE":
        return [_line_segment(entity)]

    if entity_type == "LWPOLYLINE":
        return _polyline_segments(getattr(entity, "get_points", lambda: [])())

    if entity_type == "POLYLINE":
        points = []
        getter = getattr(entity, "get_points", None)
        if callable(getter):
            points = getter()
        if not points and hasattr(entity, "vertices"):
            vertices = list(entity.vertices)
            points = [tuple(vertex.dxf.insert) for vertex in vertices if hasattr(vertex, "dxf")]
        return _polyline_segments(points)

    return []


def _line_segment(entity: Any) -> tuple[tuple[float, float], tuple[float, float]]:
    start = _coerce_point(getattr(entity.dxf, "start", None))
    end = _coerce_point(getattr(entity.dxf, "end", None))
    return start, end


def _polyline_segments(points: list[Any]) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    if not points:
        return []

    normalized_points = [_coerce_point(point) for point in points]
    if len(normalized_points) < 2:
        return []

    segments = []
    for index in range(len(normalized_points) - 1):
        if normalized_points[index] == normalized_points[index + 1]:
            continue
        segments.append((normalized_points[index], normalized_points[index + 1]))

    if len(normalized_points) >= 3:
        if normalized_points[0] == normalized_points[-1]:
            return segments

        if normalized_points[-1] != normalized_points[0]:
            segments.append((normalized_points[-1], normalized_points[0]))

    return segments


def _coerce_point(value: Any) -> tuple[float, float]:
    if value is None:
        return (0.0, 0.0)

    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return (float(value[0]), float(value[1]))

    if hasattr(value, "x") and hasattr(value, "y"):
        return (float(value.x), float(value.y))

    return (0.0, 0.0)
