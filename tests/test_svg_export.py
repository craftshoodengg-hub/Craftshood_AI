"""Tests for SVG export functionality - Part 1."""
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
from building_model_v2.entities_opening import Door, Window
from building_model_v2.types import RoomType, WallType, ColumnType, StairType, DoorType
from building_model_v2.validation.cross_entity_validator import BuildingModel
from building_model_v2.export.drawing_entities import (
    LineEntity, PolylineEntity, PolygonEntity, CircleEntity,
    ArcEntity, TextEntity, DimensionEntity, HatchEntity,
)
from building_model_v2.export.drawing_model import DrawingModel, DrawingBounds
from building_model_v2.export.drawing_builder import build_drawing_model
from building_model_v2.export.svg_exporter import export_svg, export_svg_to_string


@pytest.fixture
def sample_building():
    building = Building.create(name="Test Building", floor_ids=("f1",))
    floor = Floor.create(name="F1", level=0, room_ids=frozenset({"r1", "r2"}))
    r1 = Room.create(vertices=[(0,0),(10,0),(10,10),(0,10)], room_type=RoomType.LIVING)
    r2 = Room.create(vertices=[(10,0),(20,0),(20,10),(10,10)], room_type=RoomType.BEDROOM)
    w1 = Wall.create(start=(0,0), end=(10,0), wall_type=WallType.EXTERIOR)
    col = Column.create(location=Point2D(x=5, y=5), size=1.0, column_type=ColumnType.SQUARE)
    stair = Stair.create(start=(0,0), end=(5,0), width=3.0, stair_type=StairType.STRAIGHT)
    door = Door.create(location=Point2D(x=5, y=0), width=3.0, door_type=DoorType.SINGLE_LEAF)
    window = Window.create(location=Point2D(x=15, y=0), width=4.0)
    return BuildingModel(
        building=building, floors={"f1": floor},
        rooms={"r1": r1, "r2": r2}, walls={"w1": w1},
        columns={"c1": col}, stairs={"s1": stair},
        doors={"d1": door}, windows={"w1": window}, relationships=[],
    )


@pytest.fixture
def sample_drawing(sample_building):
    return build_drawing_model(sample_building)


class TestSVGExport:
    def test_export_to_string_returns_string(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert isinstance(svg, str)
        assert len(svg) > 0

    def test_svg_has_xml_header(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert svg.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_svg_has_svg_tag(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "<svg" in svg
        assert svg.strip().endswith("</svg>")

    def test_svg_has_viewbox(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "viewBox=" in svg

    def test_svg_has_layer_groups(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "layer-" in svg
        assert "<g id=" in svg

    def test_svg_has_line_elements(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "<line" in svg

    def test_svg_has_text_elements(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "<text" in svg
        assert "Living" in svg
        assert "Bedroom" in svg

    def test_svg_has_circle_elements(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "<circle" in svg

    def test_svg_has_polygon_elements(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "<polygon" in svg

    def test_svg_deterministic(self, sample_drawing):
        svg1 = export_svg_to_string(sample_drawing)
        svg2 = export_svg_to_string(sample_drawing)
        assert svg1 == svg2

    def test_export_to_file(self, sample_drawing):
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            path = f.name
        try:
            result = export_svg(sample_drawing, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
            with open(path) as f:
                content = f.read()
            assert "<svg" in content
        finally:
            os.unlink(path)

    def test_svg_responsive(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert 'width="100%"' in svg
        assert 'height="100%"' in svg

    def test_svg_has_north_arrow(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert ">N<" in svg

    def test_svg_has_scale_bar(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "10 ft" in svg

    def test_svg_has_title_block(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "Test Building" in svg
        assert "Craftshood AI" in svg

    def test_svg_has_dimensions(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "20 ft" in svg or "20.00 ft" in svg

    def test_svg_background(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert "background-color:#FFFFFF" in svg

    def test_empty_model_svg(self):
        dm = DrawingModel.empty()
        svg = export_svg_to_string(dm)
        assert "<svg" in svg
        assert "viewBox=" in svg

    def test_svg_namespace(self, sample_drawing):
        svg = export_svg_to_string(sample_drawing)
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg


class TestSVGEdgeCases:
    def test_svg_with_arc_entity(self):
        dm = DrawingModel(
            entities=(ArcEntity(cx=0, cy=0, radius=5, start_angle=0, end_angle=90),),
            bounds=DrawingBounds(-10, -10, 10, 10),
        )
        svg = export_svg_to_string(dm)
        assert "<path" in svg

    def test_svg_with_hatch_entity(self):
        dm = DrawingModel(
            entities=(HatchEntity(points=((0,0),(1,0),(1,1),(0,1))),),
            bounds=DrawingBounds(-1, -1, 2, 2),
        )
        svg = export_svg_to_string(dm)
        assert "<polygon" in svg

    def test_svg_escapes_xml(self):
        dm = DrawingModel(
            entities=(TextEntity(x=0, y=0, text="A & B < C > D"),),
            bounds=DrawingBounds(-5, -5, 5, 5),
        )
        svg = export_svg_to_string(dm)
        assert "A &amp; B &lt; C &gt; D" in svg
        assert "A & B" not in svg

    def test_svg_with_rotated_text(self):
        dm = DrawingModel(
            entities=(TextEntity(x=0, y=0, text="Rotated", rotation=45),),
            bounds=DrawingBounds(-5, -5, 5, 5),
        )
        svg = export_svg_to_string(dm)
        assert 'transform="rotate(45' in svg

    def test_svg_with_polyline_open(self):
        dm = DrawingModel(
            entities=(PolylineEntity(points=((0,0),(1,1),(2,0)), closed=False),),
            bounds=DrawingBounds(-1, -1, 3, 2),
        )
        svg = export_svg_to_string(dm)
        assert "<polyline" in svg

    def test_svg_with_polyline_closed(self):
        dm = DrawingModel(
            entities=(PolylineEntity(points=((0,0),(1,0),(1,1),(0,1)), closed=True),),
            bounds=DrawingBounds(-1, -1, 2, 2),
        )
        svg = export_svg_to_string(dm)
        assert "<polygon" in svg


class TestBackwardCompatibility:
    def test_dxf_still_works(self, sample_building):
        from building_model_v2.export.dxf_exporter import DXFExporter
        exporter = DXFExporter()
        result = exporter.export_to_string(sample_building)
        assert "EOF" in result
        assert "SECTION" in result

    def test_export_building_convenience(self, sample_building):
        from building_model_v2.export.dxf_exporter import export_building
        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
            path = f.name
        try:
            result = export_building(sample_building, path)
            assert os.path.exists(result)
            assert os.path.getsize(result) > 0
        finally:
            os.unlink(path)

    def test_drawing_settings_unchanged(self):
        from building_model_v2.export.drawing_settings import DrawingSettings
        s = DrawingSettings.default()
        assert s.paper_size.value == "A3"
        d = s.to_dict()
        assert d["paper_size"] == "A3"

    def test_dxf_deterministic(self, sample_building):
        from building_model_v2.export.dxf_exporter import DXFExporter
        exporter = DXFExporter()
        r1 = exporter.export_to_string(sample_building)
        r2 = exporter.export_to_string(sample_building)
        assert r1 == r2
