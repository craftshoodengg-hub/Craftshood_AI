"""Production-ready rule-based CAD text intelligence for DXF files."""

from .json_exporter import CADAnalysis, analysis_to_dict, analyze_dxf, export_analysis_json, export_dxf_json
from .plot_detector import PlotDimension, detect_plot_dimensions
from .room_detector import (
    Detection,
    detect_built_up_areas,
    detect_floor_titles,
    detect_road_labels,
    detect_rooms,
)
from .text_extractor import Point2D, TextEntity, extract_text_entities

__all__ = [
    "CADAnalysis",
    "Detection",
    "PlotDimension",
    "Point2D",
    "TextEntity",
    "analysis_to_dict",
    "analyze_dxf",
    "detect_built_up_areas",
    "detect_floor_titles",
    "detect_plot_dimensions",
    "detect_road_labels",
    "detect_rooms",
    "export_analysis_json",
    "export_dxf_json",
    "extract_text_entities",
]
