"""Tests for dimension engine - Part 1."""
from __future__ import annotations
import pytest
from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_wall import Wall
from building_model_v2.entities_column import Column
from building_model_v2.entities_opening import Door, Window
from building_model_v2.types import RoomType, WallType, ColumnType, DoorType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.export.annotation_settings import AnnotationSettings
from building_model_v2.export.dimension_engine import (
    generate_all_dimensions, generate_overall_dimensions,
    generate_room_dimensions, generate_door_window_dimensions,
    generate_column_spacing_dimensions, generate_wall_thickness_dimensions,
)
from building_model_v2.export.annotation_entities import LinearDimension, AlignedDimension
from building_model_v2.export.room_schedule import generate_room_schedule, RoomSchedule, RoomScheduleEntry


@pytest.fixture
def sample_building():
    building = Building.create(name="Test Building", floor_ids=("f1",))
    floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1", "r2"}))
    r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
    r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.BEDROOM)
    w1 = Wall.create(start=(0,0), end=(10,0), wall_type=WallType.EXTERIOR)
    col1 = Column.create(location=Point2D(x=5, y=5), size=1.0, column_type=ColumnType.SQUARE)
    col2 = Column.create(location=Point2D(x=15, y=5), size=1.0, column_type=ColumnType.SQUARE)
    door = Door.create(location=Point2D(x=5, y=0), width=3.0, door_type=DoorType.SINGLE_LEAF)
    window = Window.create(location=Point2D(x=15, y=0), width=4.0)
    return BuildingModel(
        building=building, floors={"f1": floor},
        rooms={"r1": r1, "r2": r2}, walls={"w1": w1},
        columns={"c1": col1, "c2": col2}, stairs={},
        doors={"d1": door}, windows={"w1": window}, relationships=[],
    )


@pytest.fixture
def empty_building():
    return BuildingModel()


@pytest.fixture
def default_settings():
    return AnnotationSettings.default()


class TestOverallDimensions:
    def test_generated(self, sample_building, default_settings):
        dims = generate_overall_dimensions(sample_building, default_settings)
        assert len(dims) == 2
    def test_empty_model(self, empty_building, default_settings):
        dims = generate_overall_dimensions(empty_building, default_settings)
        assert len(dims) == 0
    def test_labels_correct(self, sample_building, default_settings):
        dims = generate_overall_dimensions(sample_building, default_settings)
        labels = [d.label for d in dims]
        assert "20 ft" in labels
        assert "10 ft" in labels


class TestRoomDimensions:
    def test_generated(self, sample_building, default_settings):
        dims = generate_room_dimensions(sample_building, default_settings)
        assert len(dims) >= 4


class TestDoorWindowDimensions:
    def test_door_dims(self, sample_building, default_settings):
        dims = generate_door_window_dimensions(sample_building, default_settings)
        door_dims = [d for d in dims if "3 ft" in d.label]
        assert len(door_dims) >= 1
    def test_window_dims(self, sample_building, default_settings):
        dims = generate_door_window_dimensions(sample_building, default_settings)
        win_dims = [d for d in dims if "4 ft" in d.label]
        assert len(win_dims) >= 1


class TestColumnSpacingDimensions:
    def test_generated(self, sample_building, default_settings):
        dims = generate_column_spacing_dimensions(sample_building, default_settings)
        assert len(dims) >= 1
    def test_single_column_no_dims(self, default_settings):
        building = Building.create(name="Single", floor_ids=("f1",))
        col = Column.create(location=Point2D(x=5, y=5), size=1.0)
        model = BuildingModel(building=building, rooms={}, walls={}, columns={"c1": col})
        dims = generate_column_spacing_dimensions(model, default_settings)
        assert len(dims) == 0


class TestWallThicknessDimensions:
    def test_generated(self, sample_building, default_settings):
        dims = generate_wall_thickness_dimensions(sample_building, default_settings)
        assert len(dims) >= 1


class TestAllDimensions:
    def test_generated(self, sample_building, default_settings):
        dims = generate_all_dimensions(sample_building, default_settings)
        assert len(dims) > 0
        assert all(isinstance(d, (LinearDimension, AlignedDimension)) for d in dims)
    def test_deterministic(self, sample_building, default_settings):
        d1 = generate_all_dimensions(sample_building, default_settings)
        d2 = generate_all_dimensions(sample_building, default_settings)
        assert d1 == d2
    def test_empty_when_disabled(self, sample_building):
        settings = AnnotationSettings(show_dimensions=False)
        dims = generate_all_dimensions(sample_building, settings)
        assert len(dims) == 0
    def test_precision(self, sample_building):
        settings = AnnotationSettings(label_precision=2)
        dims = generate_overall_dimensions(sample_building, settings)
        for d in dims:
            if d.label:
                assert "." in d.label


class TestRoomSchedule:
    def test_generated(self, sample_building):
        schedule = generate_room_schedule(sample_building)
        assert isinstance(schedule, RoomSchedule)
        assert len(schedule.entries) == 2
    def test_empty_model(self, empty_building):
        schedule = generate_room_schedule(empty_building)
        assert len(schedule.entries) == 0
        assert schedule.total_area == 0.0
    def test_total_area(self, sample_building):
        schedule = generate_room_schedule(sample_building)
        assert schedule.total_area == 200.0
    def test_building_name(self, sample_building):
        schedule = generate_room_schedule(sample_building)
        assert schedule.building_name == "Test Building"
    def test_entry_fields(self, sample_building):
        schedule = generate_room_schedule(sample_building)
        entry = schedule.entries[0]
        assert entry.room_number.startswith("R")
        assert entry.room_name in ("Living", "Bedroom")
        assert entry.area > 0
        assert entry.perimeter > 0
        assert entry.privacy in ("High", "Medium", "Low")
        assert entry.natural_light in ("Good", "Moderate", "Low")
        assert entry.ventilation in ("Good", "Moderate", "Low")
    def test_privacy_classification(self):
        building = Building.create(name="Test", floor_ids=("f1",))
        r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.BEDROOM)
        r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.LIVING)
        model = BuildingModel(building=building, rooms={"r1": r1, "r2": r2})
        schedule = generate_room_schedule(model)
        entries = {e.room_name: e for e in schedule.entries}
        assert entries["Bedroom"].privacy == "High"
        assert entries["Living"].privacy == "Low"
    def test_round_trip(self, sample_building):
        schedule = generate_room_schedule(sample_building)
        schedule2 = RoomSchedule.from_dict(schedule.to_dict())
        assert len(schedule2.entries) == len(schedule.entries)
        assert schedule2.total_area == schedule.total_area
    def test_entry_round_trip(self, sample_building):
        schedule = generate_room_schedule(sample_building)
        entry = schedule.entries[0]
        entry2 = RoomScheduleEntry.from_dict(entry.to_dict())
        assert entry == entry2
    def test_deterministic(self, sample_building):
        s1 = generate_room_schedule(sample_building)
        s2 = generate_room_schedule(sample_building)
        assert s1.to_dict() == s2.to_dict()
    def test_large_building_schedule(self):
        building = Building.create(name="Large", floor_ids=("f1",))
        rooms = {}
        for i in range(20):
            rid = f"r{i}"
            x = (i % 5) * 12
            y = (i // 5) * 12
            rooms[rid] = Room.create(
                vertices=[(x,y),(x+10,y),(x+10,y+10),(x,y+10)],
                room_type=RoomType.LIVING,
            )
        model = BuildingModel(building=building, rooms=rooms)
        schedule = generate_room_schedule(model)
        assert len(schedule.entries) == 20
        assert schedule.total_area == 20 * 100.0


class TestBackwardCompatibility:
    def test_dxf_still_works(self, sample_building):
        from building_model_v2.export.dxf_exporter import DXFExporter
        exporter = DXFExporter()
        result = exporter.export_to_string(sample_building)
        assert "EOF" in result
        assert "SECTION" in result
    def test_svg_still_works(self, sample_building):
        from building_model_v2.export.drawing_builder import build_drawing_model
        from building_model_v2.export.svg_exporter import export_svg_to_string
        dm = build_drawing_model(sample_building)
        svg = export_svg_to_string(dm)
        assert "<svg" in svg
    def test_drawing_settings_unchanged(self):
        from building_model_v2.export.drawing_settings import DrawingSettings
        s = DrawingSettings.default()
        assert s.paper_size.value == "A3"
