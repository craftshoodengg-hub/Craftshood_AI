"""Unit tests for Vastu geometry, grid, and analyzer."""
from __future__ import annotations
import math
import pytest
from shapely.geometry import Polygon, box
from building_model_v2.vastu.vastu_grid import VastuCell, VastuGrid
from building_model_v2.vastu.vastu_geometry import (
    calculate_building_center,
    calculate_room_centroid,
    calculate_room_direction,
    calculate_plot_rotation,
    rotate_point,
    determine_zone,
    zone_to_vastu_zone,
)
from building_model_v2.vastu.vastu_analyzer import VastuAnalyzer
from building_model_v2.vastu.vastu_direction import VastuDirection
from building_model_v2.vastu.vastu_metadata import VastuMetadata
from building_model_v2.vastu.vastu_zone import VastuZone
from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.types import RoomType
from building_model_v2.validation.cross_entity_validator import BuildingModel


class TestGeometry:
    def test_building_center_square(self):
        poly = box(0, 0, 10, 10)
        c = calculate_building_center(poly)
        assert c is not None and abs(c.x - 5.0) < 0.01 and abs(c.y - 5.0) < 0.01

    def test_building_center_rect(self):
        poly = box(0, 0, 20, 10)
        c = calculate_building_center(poly)
        assert c is not None and abs(c.x - 10.0) < 0.01 and abs(c.y - 5.0) < 0.01

    def test_room_centroid(self):
        c = calculate_room_centroid(box(0, 0, 10, 10))
        assert c is not None and abs(c.x - 5.0) < 0.01

    def test_room_centroid_empty(self):
        assert calculate_room_centroid(Polygon()) is None

    def test_room_direction_south_screen(self):
        assert calculate_room_direction(Point2D(x=0, y=10), Point2D(x=0, y=0)) == VastuDirection.SOUTH

    def test_room_direction_east(self):
        assert calculate_room_direction(Point2D(x=10, y=0), Point2D(x=0, y=0)) == VastuDirection.EAST

    def test_room_direction_north_screen(self):
        assert calculate_room_direction(Point2D(x=0, y=-10), Point2D(x=0, y=0)) == VastuDirection.NORTH

    def test_room_direction_west(self):
        assert calculate_room_direction(Point2D(x=-10, y=0), Point2D(x=0, y=0)) == VastuDirection.WEST

    def test_plot_rotation(self):
        assert calculate_plot_rotation(0.0) == 0.0
        assert calculate_plot_rotation(90.0) == 90.0
        assert calculate_plot_rotation(360.0) == 0.0
        assert calculate_plot_rotation(450.0) == 90.0

    def test_rotate_point(self):
        p = Point2D(x=1, y=0)
        r90 = rotate_point(p, 90)
        assert abs(r90.x) < 0.01 and abs(r90.y - 1.0) < 0.01
        r180 = rotate_point(p, 180)
        assert abs(r180.x + 1.0) < 0.01 and abs(r180.y) < 0.01

    def test_determine_zone(self):
        assert determine_zone(Point2D(x=0, y=10), Point2D(x=0, y=0)) == VastuDirection.SOUTH
        assert determine_zone(Point2D(x=10, y=-10), Point2D(x=0, y=0)) == VastuDirection.NORTH_EAST

    def test_zone_to_vastu_zone(self):
        assert zone_to_vastu_zone(VastuDirection.NORTH) == VastuZone.NORTH
        assert zone_to_vastu_zone(VastuDirection.SOUTH_EAST) == VastuZone.AGNEYA
        assert zone_to_vastu_zone(VastuDirection.CENTER) == VastuZone.BRAHMASTHAN

    def test_geometry_deterministic(self):
        poly = box(0, 0, 10, 10)
        assert calculate_building_center(poly) == calculate_building_center(poly)


class TestVastuGrid:
    def test_3x3_generation(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        assert grid.cell_count == 9

    def test_center_cell(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        assert grid.center_cell.zone == VastuZone.BRAHMASTHAN
        assert grid.center_cell.row == 1 and grid.center_cell.column == 1

    def test_get_cell(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        assert grid.get_cell(0, 0).zone == VastuZone.VAYAVYA
        assert grid.get_cell(5, 5) is None

    def test_get_zone(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        assert grid.get_zone(VastuZone.AGNEYA).zone == VastuZone.AGNEYA

    def test_dimensions(self):
        grid = VastuGrid.generate(box(0, 0, 30, 20))
        assert abs(grid.width - 30.0) < 0.01 and abs(grid.height - 20.0) < 0.01

    def test_empty_boundary(self):
        grid = VastuGrid.generate(Polygon())
        assert grid.cell_count == 0

    def test_serialization(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        data = grid.to_dict()
        assert data["cell_count"] == 9 and len(data["cells"]) == 9

    def test_cell_center_and_area(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        cell = grid.get_cell(0, 0)
        assert isinstance(cell.center, Point2D)
        assert abs(cell.area - 100.0) < 0.01

    def test_rectangular_grid(self):
        grid = VastuGrid.generate(box(0, 0, 60, 30))
        assert grid.cell_count == 9 and abs(grid.width - 60.0) < 0.01

    def test_zone_layout(self):
        grid = VastuGrid.generate(box(0, 0, 30, 30))
        assert grid.get_cell(0, 2).zone == VastuZone.ISHANYA
        assert grid.get_cell(2, 0).zone == VastuZone.NAIRUTYA
        assert grid.get_cell(2, 2).zone == VastuZone.AGNEYA
        assert grid.get_cell(1, 0).zone == VastuZone.WEST
        assert grid.get_cell(1, 2).zone == VastuZone.EAST

class TestVastuAnalyzer:
    def test_empty_model(self):
        m = BuildingModel(building=None, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert isinstance(VastuAnalyzer().analyze(m), VastuMetadata)

    def test_building_only(self):
        b = Building.create(name="T", floor_ids=())
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).entrance_direction is None

    def test_single_room(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"r"}))
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"r": r}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert isinstance(VastuAnalyzer().analyze(m), VastuMetadata)

    def test_kitchen(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"k"}))
        k = Room.create(vertices=[(20,0),(30,0),(30,10),(20,10)], room_type=RoomType.KITCHEN)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"k": k}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).kitchen_direction is not None

    def test_bedroom(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"bd"}))
        bd = Room.create(vertices=[(0,20),(10,20),(10,30),(0,30)], room_type=RoomType.BEDROOM)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"bd": bd}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).master_bedroom_direction is not None

    def test_pooja(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"p"}))
        p = Room.create(vertices=[(0,10),(10,10),(10,20),(0,20)], room_type=RoomType.UNKNOWN, metadata={"name": "Pooja Room"})
        m = BuildingModel(building=b, floors={"f": f}, rooms={"p": p}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).pooja_direction is not None

    def test_staircase(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"r"}), stair_ids=frozenset({"s"}))
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
        s = Stair.create(start=(40,0), end=(60,0), width=3.0)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"r": r}, walls={}, columns={}, stairs={"s": s}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).staircase_direction is not None

    def test_toilet(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"t"}))
        t = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.TOILET)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"t": t}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).toilet_direction is not None

    def test_entrance(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"e"}))
        e = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.CORRIDOR, metadata={"name": "Entrance"})
        m = BuildingModel(building=b, floors={"f": f}, rooms={"e": e}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).entrance_direction is not None

    def test_missing_metadata(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"r"}))
        r = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.STORAGE)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"r": r}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        res = VastuAnalyzer().analyze(m)
        assert res.entrance_direction is None and res.kitchen_direction is None

    def test_deterministic(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"k"}))
        k = Room.create(vertices=[(20,0),(30,0),(30,10),(20,10)], room_type=RoomType.KITCHEN)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"k": k}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        a = VastuAnalyzer()
        assert a.analyze(m) == a.analyze(m)

    def test_existing_metadata(self):
        b = Building.create(name="T", floor_ids=())
        b.metadata["vastu"] = VastuMetadata(entrance_direction=VastuDirection.EAST)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).entrance_direction == VastuDirection.EAST

    def test_north_rotation(self):
        b = Building.create(name="T", floor_ids=(), north_direction=45.0)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).north_rotation == 45.0

    def test_plot_facing(self):
        b = Building.create(name="T", floor_ids=(), north_direction=90.0)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        assert VastuAnalyzer().analyze(m).plot_facing == VastuDirection.EAST

    def test_multiple_rooms(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"k", "bd"}))
        k = Room.create(vertices=[(40,0),(60,0),(60,20),(40,20)], room_type=RoomType.KITCHEN)
        bd = Room.create(vertices=[(0,0),(20,0),(20,20),(0,20)], room_type=RoomType.BEDROOM)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"k": k, "bd": bd}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        res = VastuAnalyzer().analyze(m)
        assert res.kitchen_direction is not None and res.master_bedroom_direction is not None

    def test_serialization_compat(self):
        b = Building.create(name="T", floor_ids=())
        b.metadata["vastu"] = VastuMetadata(entrance_direction=VastuDirection.NORTH, kitchen_direction=VastuDirection.SOUTH_EAST)
        m = BuildingModel(building=b, floors={}, rooms={}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        res = VastuAnalyzer().analyze(m)
        d = res.to_dict()
        assert d["entrance_direction"] == "NORTH" and d["kitchen_direction"] == "SOUTH_EAST"
        assert VastuMetadata.from_dict(d) == res


class TestIntegration:
    def test_grid_on_building(self):
        grid = VastuGrid.generate(box(0, 0, 60, 40))
        assert grid.cell_count == 9 and grid.width == 60 and grid.height == 40

    def test_analyzer_with_grid(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"k"}))
        k = Room.create(vertices=[(40,0),(60,0),(60,20),(40,20)], room_type=RoomType.KITCHEN)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"k": k}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        res = VastuAnalyzer().analyze(m)
        grid = VastuGrid.generate(box(0, 0, 60, 40))
        assert grid.get_zone(VastuZone.AGNEYA) is not None and res.kitchen_direction is not None

    def test_full_workflow_deterministic(self):
        b = Building.create(name="T", floor_ids=("f",))
        f = Floor.create(name="F", level=0, room_ids=frozenset({"k", "bd", "p", "t"}))
        k = Room.create(vertices=[(40,0),(60,0),(60,20),(40,20)], room_type=RoomType.KITCHEN)
        bd = Room.create(vertices=[(0,0),(20,0),(20,20),(0,20)], room_type=RoomType.BEDROOM)
        p = Room.create(vertices=[(20,20),(40,20),(40,40),(20,40)], room_type=RoomType.UNKNOWN, metadata={"name": "Pooja"})
        t = Room.create(vertices=[(40,20),(60,20),(60,40),(40,40)], room_type=RoomType.TOILET)
        m = BuildingModel(building=b, floors={"f": f}, rooms={"k": k, "bd": bd, "p": p, "t": t}, walls={}, columns={}, stairs={}, doors={}, windows={}, relationships=[])
        a = VastuAnalyzer()
        assert a.analyze(m) == a.analyze(m)
