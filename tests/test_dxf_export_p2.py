"""Unit tests for DXF Export - Part 2."""
from __future__ import annotations
import os
import tempfile
import pytest
from building_model_v2.base import Point2D
from building_model_v2.entities_building import Building
from building_model_v2.entities_floor import Floor
from building_model_v2.entities_room import Room
from building_model_v2.entities_wall import Wall
from building_model_v2.entities_column import Column
from building_model_v2.entities_stair import Stair
from building_model_v2.types import RoomType, WallType, ColumnType, StairType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.export.dxf_exporter import (
    DXFExporter, DrawingSettings, export_building, TitleBlockData,
)


@pytest.fixture
def sample_building():
    building = Building.create(name="Test", floor_ids=("f1",))
    floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1", "r2"}))
    r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
    r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.BEDROOM)
    w1 = Wall.create(start=(0,0), end=(10,0), wall_type=WallType.EXTERIOR)
    col = Column.create(location=Point2D(x=5, y=5), size=1.0, column_type=ColumnType.SQUARE)
    stair = Stair.create(start=(0,0), end=(5,0), width=3.0, stair_type=StairType.STRAIGHT)
    return BuildingModel(
        building=building, floors={"f1": floor},
        rooms={"r1": r1, "r2": r2}, walls={"w1": w1},
        columns={"c1": col}, stairs={"s1": stair},
        doors={}, windows={}, relationships=[],
    )


class TestDXFExporter:
    def test_export_creates_file(self, sample_building):
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            path = f.name
        try:
            exporter = DXFExporter()
            result = exporter.export(sample_building, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_export_to_string(self, sample_building):
        exporter = DXFExporter()
        result = exporter.export_to_string(sample_building)
        assert isinstance(result, str)
        assert "EOF" in result
        assert "SECTION" in result

    def test_export_with_settings(self, sample_building):
        settings = DrawingSettings(show_grid=False, show_dimensions=False,
                                   show_north_arrow=False, show_title_block=False)
        exporter = DXFExporter(settings)
        result = exporter.export_to_string(sample_building)
        assert "LAYER" in result

    def test_export_empty_model(self):
        model = BuildingModel()
        exporter = DXFExporter()
        result = exporter.export_to_string(model)
        assert "EOF" in result

    def test_export_building_convenience(self, sample_building):
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            path = f.name
        try:
            result = export_building(sample_building, path)
            assert os.path.exists(result)
        finally:
            os.unlink(path)

    def test_deterministic_output(self, sample_building):
        exporter = DXFExporter()
        r1 = exporter.export_to_string(sample_building)
        r2 = exporter.export_to_string(sample_building)
        assert r1 == r2

    def test_custom_settings(self, sample_building):
        settings = DrawingSettings(show_grid=True, show_dimensions=True,
                                   show_north_arrow=True, show_title_block=True,
                                   show_room_labels=True, show_room_areas=True)
        exporter = DXFExporter(settings)
        result = exporter.export_to_string(sample_building)
        assert len(result) > 0
