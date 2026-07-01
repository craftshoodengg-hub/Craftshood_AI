"""DWG dataset analyzer for CAD convention summarization."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import ezdxf

from .ezdxf_feature_extractor import EzDXFFeatureExtractor


class DatasetAnalyzer:
    """Analyze a dataset of DWG/DXF files for CAD conventions."""

    def __init__(self, extractor: EzDXFFeatureExtractor | None = None) -> None:
        self.extractor = extractor if extractor is not None else EzDXFFeatureExtractor()

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
            "entity_totals": Counter(),
            "layer_names": Counter(),
            "block_names": Counter(),
            "text_values": Counter(),
            "file_summaries": [],
        }

        for file_path in file_paths:
            result = self.analyze_file(str(file_path))
            if result is None:
                summary["files_failed"] += 1
                continue

            summary["files_scanned"] += 1
            self._safe_increment(summary["entity_totals"], "entity_count", result["entity_count"])

            for layer in result["layers"]:
                self._safe_increment(summary["layer_names"], layer, 1)
            for block in result["blocks"]:
                self._safe_increment(summary["block_names"], block, 1)
            for text in result["texts"]:
                self._safe_increment(summary["text_values"], text, 1)

            summary["file_summaries"].append(
                {
                    "file_path": result["file_path"],
                    "entity_count": result["entity_count"],
                    "layers": sorted(set(result["layers"])),
                    "blocks": sorted(set(result["blocks"])),
                    "texts": result["texts"],
                }
            )

        return {
            "files_scanned": summary["files_scanned"],
            "files_failed": summary["files_failed"],
            "entity_totals": dict(summary["entity_totals"]),
            "layer_names": dict(summary["layer_names"]),
            "block_names": dict(summary["block_names"]),
            "text_values": dict(summary["text_values"]),
            "file_summaries": summary["file_summaries"],
        }

    def analyze_file(self, file_path: str) -> dict[str, Any] | None:
        try:
            document = ezdxf.readfile(file_path)
        except (ezdxf.DXFError, IOError, OSError):
            return None

        modelspace = document.modelspace()
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
        }

    def _safe_increment(self, counter: Counter[str, int], key: str, amount: int = 1) -> None:
        if key in counter:
            counter[key] += amount
        else:
            counter[key] = amount
