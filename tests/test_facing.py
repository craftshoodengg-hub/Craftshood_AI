from __future__ import annotations

import pytest
from shapely.geometry import LineString, Point, Polygon

from adjacency import RoomPolygon
from facing import (
    ExteriorWall,
    FacingConfig,
    FacingDetector,
    RoadSide,
    detect_facing,
    nearest_exterior_wall,
    road_side_from_wall,
)


def test_detects_nearest_wall_as_north_front_wall_and_front_rooms() -> None:
    result = FacingDetector().detect(_rooms(), _exterior_walls(), Point(10, 15))

    assert result == {
        "road_side": "North",
        "front_wall_id": "north-wall",
        "front_rooms": ["living", "kitchen"],
    }


def test_detects_east_side_and_only_room_touching_east_front_wall() -> None:
    result = detect_facing(_rooms(), _exterior_walls(), Point(25, 5))

    assert result == {
        "road_side": "East",
        "front_wall_id": "east-wall",
        "front_rooms": ["kitchen"],
    }


def test_wall_tolerance_allows_slightly_offset_room_boundary() -> None:
    rooms = [
        RoomPolygon("living", "Living", _box(0, 0, 10, 9.98)),
    ]
    walls = [
        ExteriorWall("north-wall", LineString([(0, 10), (10, 10)])),
    ]

    strict = FacingDetector(FacingConfig(wall_tolerance=0.01)).detect(
        rooms,
        walls,
        Point(5, 15),
    )
    tolerant = FacingDetector(FacingConfig(wall_tolerance=0.03)).detect(
        rooms,
        walls,
        Point(5, 15),
    )

    assert strict["front_rooms"] == []
    assert tolerant["front_rooms"] == ["living"]


def test_returns_unknown_when_no_exterior_walls_are_provided() -> None:
    result = FacingDetector().detect(_rooms(), [], Point(10, 15))

    assert result == {
        "road_side": "Unknown",
        "front_wall_id": None,
        "front_rooms": [],
    }


def test_road_side_helpers_use_wall_midpoint_to_road_vector() -> None:
    north_wall = ExteriorWall("north-wall", LineString([(0, 10), (20, 10)]))

    assert nearest_exterior_wall(_exterior_walls(), Point(10, 15)).wall_id == "north-wall"
    assert road_side_from_wall(north_wall.geometry, Point(10, 15)) == RoadSide.NORTH
    assert road_side_from_wall(north_wall.geometry, Point(10, 10)) == RoadSide.UNKNOWN


def test_duplicate_wall_ids_are_rejected() -> None:
    walls = [
        ExteriorWall("north-wall", LineString([(0, 10), (20, 10)])),
        ExteriorWall("north-wall", LineString([(0, 0), (20, 0)])),
    ]

    with pytest.raises(ValueError, match="Duplicate wall_id"):
        FacingDetector().detect(_rooms(), walls, Point(10, 15))


def _rooms() -> list[RoomPolygon]:
    return [
        RoomPolygon("living", "Living", _box(0, 0, 10, 10)),
        RoomPolygon("kitchen", "Kitchen", _box(10, 0, 20, 10)),
        RoomPolygon("bed", "Bed room", _box(0, -10, 10, 0)),
    ]


def _exterior_walls() -> list[ExteriorWall]:
    return [
        ExteriorWall("south-wall", LineString([(0, -10), (20, -10)])),
        ExteriorWall("east-wall", LineString([(20, -10), (20, 10)])),
        ExteriorWall("north-wall", LineString([(20, 10), (0, 10)])),
        ExteriorWall("west-wall", LineString([(0, 10), (0, -10)])),
    ]


def _box(min_x: float, min_y: float, max_x: float, max_y: float) -> Polygon:
    return Polygon(
        [
            (min_x, min_y),
            (max_x, min_y),
            (max_x, max_y),
            (min_x, max_y),
            (min_x, min_y),
        ]
    )
