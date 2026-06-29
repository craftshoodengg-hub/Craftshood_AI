"""Export package for Building Model v2.

Provides:
- DXFExporter: DXF file export
- DrawingModel: Unified intermediate representation
- DrawingBuilder: BuildingModel -> DrawingModel conversion
- SVG export: DrawingModel -> SVG string/file
- AnnotationEngine: Professional annotation generation
- DimensionEngine: Automatic dimension generation
- RoomSchedule: Room schedule generation
- PDF Report: Professional multi-page PDF documentation
"""
from .dxf_exporter import DXFExporter, export_building
from .drawing_settings import DrawingSettings, PaperSize, DrawingUnits
from .drawing_model import DrawingModel, DrawingLayer, DrawingBounds
from .drawing_builder import build_drawing_model
from .svg_exporter import export_svg, export_svg_to_string
from .annotation_settings import AnnotationSettings
from .annotation_engine import generate_all_annotations
from .dimension_engine import generate_all_dimensions
from .room_schedule import generate_room_schedule, RoomSchedule, RoomScheduleEntry
from .pdf_report import generate_pdf_report, generate_pdf_report_to_bytes
from .report_metadata import ReportMetadata

__all__ = [
    "DXFExporter", "export_building",
    "DrawingSettings", "PaperSize", "DrawingUnits",
    "DrawingModel", "DrawingLayer", "DrawingBounds",
    "build_drawing_model",
    "export_svg", "export_svg_to_string",
    "AnnotationSettings",
    "generate_all_annotations",
    "generate_all_dimensions",
    "generate_room_schedule", "RoomSchedule", "RoomScheduleEntry",
    "generate_pdf_report", "generate_pdf_report_to_bytes",
    "ReportMetadata",
]
