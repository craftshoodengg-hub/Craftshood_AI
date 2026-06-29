"""Unit tests for DXF Export - Part 1."""
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
    DXFExporter, DrawingSettings, export_building,
    TitleBlockData, Color, DXFStyle, DXFLayer,
    ALL_LAYERS, ALL_STYLES, LAYER_WALL, LAYER_DOOR, LAYER_WINDOW,
    LAYER_STAIR, LAYER_COLUMN, LAYER_GRID, LAYER_TEXT, LAYER_DIM,
    STYLE_MAP, LAYER_MAP,
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


class TestDXFStyles:
    def test_all_styles_present(self):
        assert len(ALL_STYLES) == 8

    def test_style_map(self):
        assert "A-WALL" in STYLE_MAP
        assert "A-DOOR" in STYLE_MAP

    def test_color_aci(self):
        assert Color(0, 0, 0).aci == 7
        assert Color(255, 0, 0).aci == 1
        assert Color(0, 0, 255).aci == 5


class TestDXFLayers:
    def test_all_layers_present(self):
        assert len(ALL_LAYERS) == 10

    def test_layer_map(self):
        assert "A-WALL" in LAYER_MAP
        assert "A-TITLE" in LAYER_MAP

    def test_layer_wall(self):
        assert LAYER_WALL.name == "A-WALL"
        assert LAYER_WALL.color.aci == 7


class TestDrawingSettings:
    def test_default(self):
        s = DrawingSettings.default()
        assert s.paper_size.value == "A3"
        assert s.show_grid is True
        assert s.show_dimensions is True

    def test_to_dict(self):
        s = DrawingSettings.default()
        d = s.to_dict()
        assert d["paper_size"] == "A3"
        assert d["show_grid"] is True

    def test_from_dict(self):
        d = {"paper_size": "A2", "units": "meters", "scale": 2.0,
             "text_height": 0.3, "show_grid": False, "show_dimensions": False,
             "show_title_block": False, "show_north_arrow": False,
             "show_room_labels": False, "show_room_areas": False,
             "layer_visibility": {}}
        s = DrawingSettings.from_dict(d)
        assert s.paper_size.value == "A2"
        assert s.show_grid is False


class TestTitleBlockData:
    def test_defaults(self):
        tb = TitleBlockData()
        assert tb.project_name == "Craftshood AI Project"
        assert tb.drawn_by == "Craftshood AI"

    def test_to_dict(self):
        tb = TitleBlockData()
        d = tb.to_dict()
        assert "project_name" in d
        assert "date" in d

    def test_from_dict(self):
        d = {"project_name": "Custom", "drawn_by": "Test"}
        tb = TitleBlockData.from_dict(d)
        assert tb.project_name == "Custom"
