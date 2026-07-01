from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from building_model_v2.pipeline.dwg_knowledge import RoomPolygonBuilder


class FakeDxf:
    def __init__(self, *, layer: str = "0", start=None, end=None, insert=(0.0, 0.0), text: str = "") -> None:
        self.layer = layer
        self.start = start
        self.end = end
        self.insert = insert
        self.text = text


class FakeLineEntity:
    def __init__(self, start, end, layer: str = "Wall") -> None:
        self._dxftype = "LINE"
        self._dxf = FakeDxf(layer=layer, start=start, end=end)

    def dxftype(self) -> str:
        return self._dxftype

    @property
    def dxf(self) -> FakeDxf:
        return self._dxf


class FakeLwPolylineEntity:
    def __init__(self, points, layer: str = "Wall") -> None:
        self._dxftype = "LWPOLYLINE"
        self._points = list(points)
        self._dxf = FakeDxf(layer=layer)

    def dxftype(self) -> str:
        return self._dxftype

    def get_points(self):
        return self._points

    @property
    def dxf(self) -> FakeDxf:
        return self._dxf


class FakeTextEntity:
    def __init__(self, text: str, insert, layer: str = "Text") -> None:
        self._dxftype = "TEXT"
        self._dxf = FakeDxf(layer=layer, insert=insert, text=text)

    def dxftype(self) -> str:
        return self._dxftype

    @property
    def dxf(self) -> FakeDxf:
        return self._dxf


class FakeDocument:
    def __init__(self, entities) -> None:
        self._entities = list(entities)

    def modelspace(self):
        return self._entities


def test_builds_rectangle_room_polygon() -> None:
    entities = [
        FakeLineEntity((0.0, 0.0), (10.0, 0.0)),
        FakeLineEntity((10.0, 0.0), (10.0, 10.0)),
        FakeLineEntity((10.0, 10.0), (0.0, 10.0)),
        FakeLineEntity((0.0, 10.0), (0.0, 0.0)),
        FakeTextEntity("Bedroom", (5.0, 5.0)),
    ]

    rooms = RoomPolygonBuilder.build(FakeDocument(entities))

    assert len(rooms) == 1
    room = rooms[0]
    assert room["room_type"] == "Bedroom"
    assert room["raw_label"] == "Bedroom"
    assert room["area"] == pytest.approx(100.0)
    assert room["perimeter"] == pytest.approx(40.0)
    assert room["centroid"] == pytest.approx((5.0, 5.0))
    assert Polygon(room["polygon"]).area == pytest.approx(100.0)


def test_builds_l_shaped_room_polygon() -> None:
    entities = [
        FakeLineEntity((0.0, 0.0), (8.0, 0.0)),
        FakeLineEntity((8.0, 0.0), (8.0, 4.0)),
        FakeLineEntity((8.0, 4.0), (4.0, 4.0)),
        FakeLineEntity((4.0, 4.0), (4.0, 8.0)),
        FakeLineEntity((4.0, 8.0), (0.0, 8.0)),
        FakeLineEntity((0.0, 8.0), (0.0, 0.0)),
        FakeTextEntity("Kitchen", (2.0, 2.0)),
    ]

    rooms = RoomPolygonBuilder.build(FakeDocument(entities))

    assert len(rooms) == 1
    assert rooms[0]["room_type"] == "Kitchen"
    assert Polygon(rooms[0]["polygon"]).area == pytest.approx(48.0)


def test_builds_multiple_adjacent_rooms() -> None:
    entities = [
        FakeLineEntity((0.0, 0.0), (10.0, 0.0)),
        FakeLineEntity((10.0, 0.0), (10.0, 10.0)),
        FakeLineEntity((10.0, 10.0), (0.0, 10.0)),
        FakeLineEntity((0.0, 10.0), (0.0, 0.0)),
        FakeLineEntity((10.0, 0.0), (20.0, 0.0)),
        FakeLineEntity((20.0, 0.0), (20.0, 10.0)),
        FakeLineEntity((20.0, 10.0), (10.0, 10.0)),
        FakeTextEntity("Bedroom", (3.0, 5.0)),
        FakeTextEntity("Living", (15.0, 5.0)),
    ]

    rooms = RoomPolygonBuilder.build(FakeDocument(entities))

    assert len(rooms) == 2
    room_types = {room["room_type"] for room in rooms}
    assert room_types == {"Bedroom", "Living"}


def test_skips_room_label_that_is_outside_polygon() -> None:
    entities = [
        FakeLineEntity((0.0, 0.0), (4.0, 0.0)),
        FakeLineEntity((4.0, 0.0), (4.0, 4.0)),
        FakeLineEntity((4.0, 4.0), (0.0, 4.0)),
        FakeLineEntity((0.0, 4.0), (0.0, 0.0)),
        FakeTextEntity("Bedroom", (10.0, 10.0)),
    ]

    rooms = RoomPolygonBuilder.build(FakeDocument(entities))

    assert rooms == []


def test_ignores_open_or_invalid_polygons() -> None:
    entities = [
        FakeLineEntity((0.0, 0.0), (4.0, 0.0)),
        FakeLineEntity((4.0, 0.0), (4.0, 4.0)),
        FakeLineEntity((4.0, 4.0), (0.0, 0.0)),
        FakeTextEntity("Bedroom", (1.0, 1.0)),
    ]

    rooms = RoomPolygonBuilder.build(FakeDocument(entities))

    assert rooms == []


def test_returns_empty_for_empty_drawing() -> None:
    rooms = RoomPolygonBuilder.build(FakeDocument([]))

    assert rooms == []


def test_supports_lwpolyline_entities() -> None:
    entities = [
        FakeLwPolylineEntity([(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0), (0.0, 0.0)]),
        FakeTextEntity("Bathroom", (2.0, 2.0)),
    ]

    rooms = RoomPolygonBuilder.build(FakeDocument(entities))

    assert len(rooms) == 1
    assert rooms[0]["room_type"] == "Toilet"
    assert Polygon(rooms[0]["polygon"]).area == pytest.approx(16.0)
