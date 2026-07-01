"""DWG dataset analyzer for CAD convention summarization."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import ezdxf

from .dwg_conversion_guide import (
    recommended_converted_folder,
    conversion_instructions,
    validate_converted_folder,
)
from .ezdxf_feature_extractor import EzDXFFeatureExtractor
from .room_label_detector import RoomLabelDetector


ROOM_TYPES = [
    "Bedroom",
    "Kitchen",
    "Living",
    "Dining",
    "Toilet",
    "Balcony",
    "Parking",
    "Utility",
    "Pooja",
    "Stair",
    "Store",
]


class DatasetAnalyzer:
    """Analyze a dataset of DWG/DXF files for CAD conventions."""

    def __init__(self, extractor: EzDXFFeatureExtractor | None = None) -> None:
        self.extractor = extractor if extractor is not None else EzDXFFeatureExtractor()
        self.room_label_detector = RoomLabelDetector()

    def analyze_directory(
        self,
        directory: str,
        recursive: bool = True,
        limit: int | None = None,
    ) -> dict[str, Any]:
        path = Path(directory)
        file_paths = sorted(
            [
                file_path
                for file_path in path.rglob("*.dxf") if recursive
            ]
            + [
                file_path
                for file_path in path.rglob("*.dwg") if recursive
            ]
        ) if recursive else sorted(
            [file_path for file_path in path.glob("*.dxf")] + [file_path for file_path in path.glob("*.dwg")]
        )

        if limit is not None:
            file_paths = file_paths[:limit]

        summary = {
            "files_scanned": 0,
            "files_failed": 0,
            "failed_files": [],
            "entity_totals": Counter(),
            "layer_names": Counter(),
            "block_names": Counter(),
            "text_values": Counter(),
            "room_totals": {room_type: 0 for room_type in ROOM_TYPES},
            "total_rooms": 0,
            "file_summaries": [],
        }

        for file_path in file_paths:
            try:
                result = self.analyze_file(str(file_path))
            except ValueError as exc:
                summary["files_failed"] += 1
                summary["failed_files"].append(
                    {"file_path": str(file_path), "reason": str(exc)}
                )
                continue

            summary["files_scanned"] += 1
            self._safe_increment(summary["entity_totals"], "entity_count", result["entity_count"])

            for layer in result["layers"]:
                self._safe_increment(summary["layer_names"], layer, 1)
            for block in result["blocks"]:
                self._safe_increment(summary["block_names"], block, 1)
            for text in result["texts"]:
                self._safe_increment(summary["text_values"], text, 1)

            room_summary = result.get("rooms", [])
            room_count = len(room_summary)
            summary["total_rooms"] += room_count
            for room in room_summary:
                room_type = room.get("room_type")
                if room_type in summary["room_totals"]:
                    summary["room_totals"][room_type] += 1

            summary["file_summaries"].append(
                {
                    "file_path": result["file_path"],
                    "entity_count": result["entity_count"],
                    "layers": sorted(set(result["layers"])),
                    "blocks": sorted(set(result["blocks"])),
                    "texts": result["texts"],
                    "rooms": room_summary,
                    "room_count": room_count,
                }
            )

        return {
            "files_scanned": summary["files_scanned"],
            "files_failed": summary["files_failed"],
            "failed_files": summary["failed_files"],
            "entity_totals": dict(summary["entity_totals"]),
            "layer_names": dict(summary["layer_names"]),
            "block_names": dict(summary["block_names"]),
            "text_values": dict(summary["text_values"]),
            "room_totals": summary["room_totals"],
            "total_rooms": summary["total_rooms"],
            "file_summaries": summary["file_summaries"],
        }

    def analyze_file(self, file_path: str) -> dict[str, Any]:
        try:
            document = ezdxf.readfile(file_path)
        except (ezdxf.DXFError, IOError, OSError) as exc:
            raise ValueError(self._failure_reason(file_path, exc)) from exc

        modelspace = document.modelspace()
        rooms = self.room_label_detector.detect(document)
        entity_count = len(modelspace)
        layers: list[str] = []
        blocks: list[str] = []
        texts: list[str] = []

        for entity in modelspace:
            if entity.dxftype() == "INSERT":
                block_name = str(entity.dxf.name) if entity.dxf.hasattr("name") else ""
                if block_name:
                    blocks.append(block_name)
            layer = str(entity.dxf.layer) if entity.dxf.hasattr("layer") else ""
            if layer:
                layers.append(layer)

            dxftype = entity.dxftype()
            if dxftype == "TEXT":
                texts.append(str(entity.dxf.text))
            elif dxftype == "MTEXT":
                texts.append(str(entity.text))

        return {
            "file_path": file_path,
            "entity_count": entity_count,
            "layers": layers,
            "blocks": blocks,
            "texts": sorted(texts),
            "rooms": rooms,
            "room_count": len(rooms),
        }

    def _failure_reason(self, file_path: str, exc: Exception) -> str:
        if Path(file_path).suffix.lower() == ".dwg":
            return (
                f"Failed to read DWG file '{file_path}'. Native DWG may require conversion to DXF "
                "before analysis."
            )
        return f"Failed to read file '{file_path}'. File may be invalid or require DXF conversion."

    def _safe_increment(self, counter: Counter[str, int], key: str, amount: int = 1) -> None:
        if key in counter:
            counter[key] += amount
        else:
            counter[key] = amount
