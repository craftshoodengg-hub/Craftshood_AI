"""High-level DXF analysis and JSON export."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

from .plot_detector import PlotDimension, detect_plot_dimensions
from .room_detector import (
    Detection,
    detect_built_up_areas,
    detect_floor_titles,
    detect_road_labels,
    detect_rooms,
)
from .text_extractor import TextEntity, extract_text_entities


@dataclass(frozen=True, slots=True)
class CADAnalysis:
    """Complete rule-based analysis result for a DXF file."""

    source_file: str
    generated_at: str
    text_entities: list[TextEntity]
    rooms: list[Detection]
    floor_titles: list[Detection]
    built_up_areas: list[Detection]
    road_labels: list[Detection]
    plot_dimensions: list[PlotDimension]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "generated_at": self.generated_at,
            "summary": {
                "text_entity_count": len(self.text_entities),
                "room_count": len(self.rooms),
                "floor_title_count": len(self.floor_titles),
                "built_up_area_count": len(self.built_up_areas),
                "road_label_count": len(self.road_labels),
                "plot_dimension_count": len(self.plot_dimensions),
            },
            "text_entities": [entity.to_dict() for entity in self.text_entities],
            "rooms": [detection.to_dict() for detection in self.rooms],
            "floor_titles": [detection.to_dict() for detection in self.floor_titles],
            "built_up_areas": [detection.to_dict() for detection in self.built_up_areas],
            "road_labels": [detection.to_dict() for detection in self.road_labels],
            "plot_dimensions": [dimension.to_dict() for dimension in self.plot_dimensions],
        }


def analyze_dxf(dxf_path: str | Path, *, include_blocks: bool = True) -> CADAnalysis:
    """Run all supported non-geometric detectors for a DXF file."""

    source = Path(dxf_path).expanduser().resolve()
    text_entities = extract_text_entities(source, include_blocks=include_blocks)
    result = CADAnalysis(
        source_file=str(source),
        generated_at=datetime.now(UTC).isoformat(),
        text_entities=text_entities,
        rooms=detect_rooms(text_entities),
        floor_titles=detect_floor_titles(text_entities),
        built_up_areas=detect_built_up_areas(text_entities),
        road_labels=detect_road_labels(text_entities),
        plot_dimensions=detect_plot_dimensions(text_entities),
    )
    logger.info("Completed CAD text analysis for {}", source.name)
    return result


def export_analysis_json(analysis: CADAnalysis, output_path: str | Path) -> Path:
    """Write an existing CADAnalysis result to a clean JSON file."""

    target = Path(output_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Exported CAD analysis JSON to {}", target)
    return target


def export_dxf_json(
    dxf_path: str | Path,
    output_path: str | Path,
    *,
    include_blocks: bool = True,
) -> Path:
    """Analyze a DXF file and export the result as JSON."""

    return export_analysis_json(
        analyze_dxf(dxf_path, include_blocks=include_blocks),
        output_path,
    )


def analysis_to_dict(analysis: CADAnalysis) -> dict[str, Any]:
    """Convert analysis to a JSON-serializable dictionary."""

    return asdict(analysis) if not hasattr(analysis, "to_dict") else analysis.to_dict()
