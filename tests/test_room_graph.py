from __future__ import annotations

import json
from pathlib import Path

import pytest

from geometry_engine import LineEntity, LogicalWall, Point2D, WallType
from room_graph import (
    AreaCalculator,
    BoundaryFinder,
    BoundaryFinderConfig,
    PolygonBuilder,
    RoomCenter,
    RoomExporter,
    RoomGraphBuilder,
)


def test_boundary_finder_casts_rays_to_nearest_walls() -> None:
    finder = BoundaryFinder(BoundaryFinderConfig(radial_ray_count=8, max_ray_length=100))

    intersections = finder.find_boundary_points(RoomCenter(5, 5), _square_walls())

    assert len(intersections) == 8
    assert {item.wall_id for item in intersections} == {
        "wall-east",
        "wall-north",
        "wall-west",
        "wall-south",
    }
    assert any(item.point.x == 10 and item.point.y == 5 for item in intersections)


def test_polygon_builder_sorts_points_clockwise_and_builds_polygon() -> None:
    center = RoomCenter(5, 5)
    intersections = BoundaryFinder(
        BoundaryFinderConfig(radial_ray_count=8, max_ray_length=100)
    ).find_boundary_points(center, _square_walls())

    polygon = PolygonBuilder().build_polygon(center, intersections)

    assert polygon.is_valid
    assert polygon.area == pytest.approx(100)
    assert polygon.length == pytest.approx(40)


def test_area_calculator_returns_room_metrics() -> None:
    center = RoomCenter(5, 5)
    intersections = BoundaryFinder(
        BoundaryFinderConfig(radial_ray_count=8, max_ray_length=100)
    ).find_boundary_points(center, _square_walls())
    polygon = PolygonBuilder().build_polygon(center, intersections)

    metrics = AreaCalculator().calculate(polygon)

    assert metrics.area == pytest.approx(100)
    assert metrics.perimeter == pytest.approx(40)
    assert metrics.centroid.x == pytest.approx(5)
    assert metrics.centroid.y == pytest.approx(5)


def test_graph_builder_returns_required_room_payload() -> None:
    result = RoomGraphBuilder(
        boundary_config=BoundaryFinderConfig(radial_ray_count=8, max_ray_length=100)
    ).build_room("Living", RoomCenter(5, 5), _square_walls())

    payload = result.to_dict()

    assert payload["room_name"] == "Living"
    assert payload["area"] == pytest.approx(100)
    assert payload["perimeter"] == pytest.approx(40)
    assert payload["centroid"] == {"x": pytest.approx(5), "y": pytest.approx(5)}
    assert set(payload["boundary_wall_ids"]) == {
        "wall-east",
        "wall-north",
        "wall-west",
        "wall-south",
    }
    assert payload["polygon"][0] == payload["polygon"][-1]


def test_room_exporter_writes_json(tmp_path: Path) -> None:
    output_path = tmp_path / "living.json"

    json_text = RoomExporter(
        boundary_config=BoundaryFinderConfig(radial_ray_count=8, max_ray_length=100)
    ).export_room_json("Living", RoomCenter(5, 5), _square_walls(), output_path)

    payload = json.loads(json_text)
    assert output_path.read_text(encoding="utf-8") == json_text
    assert payload["room_name"] == "Living"
    assert payload["area"] == pytest.approx(100)
    assert payload["centroid"]["x"] == pytest.approx(5)


def _square_walls() -> list[LogicalWall]:
    return [
        _wall("wall-south", _line("south", (0, 0), (10, 0))),
        _wall("wall-east", _line("east", (10, 0), (10, 10))),
        _wall("wall-north", _line("north", (10, 10), (0, 10))),
        _wall("wall-west", _line("west", (0, 10), (0, 0))),
    ]


def _wall(wall_id: str, line: LineEntity) -> LogicalWall:
    return LogicalWall(
        id=wall_id,
        wall_type=WallType.NINE_INCH_BRICK,
        width=0.75,
        segment_ids=(f"{wall_id}-segment",),
        line_ids=(line.id,),
        source_lines=(line,),
    )


def _line(line_id: str, start: tuple[float, float], end: tuple[float, float]) -> LineEntity:
    return LineEntity(
        id=line_id,
        start=Point2D(*start),
        end=Point2D(*end),
        length=((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5,
        angle=0,
        layer="A-WALL",
        space="test",
    )
