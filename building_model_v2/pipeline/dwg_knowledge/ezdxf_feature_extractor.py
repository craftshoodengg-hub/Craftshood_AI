"""EZDXF-based DWG feature extractor."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import ezdxf

from .dwg_metadata import DwgMetadata
from .dwg_reference import DwgReference
from .feature_extractor import BaseFeatureExtractor


class EzDXFFeatureExtractor(BaseFeatureExtractor):
    """Extract features from DXF files using ezdxf."""

    def extract_metadata(self, file_path: str) -> DwgMetadata:
        document = self._load_document(file_path)
        _ = document.modelspace()  # ensure the file is readable
        return DwgMetadata(
            file_path=file_path,
            project_type="unknown",
            tags=["dwg"],
        )

    def extract_features(self, file_path: str) -> dict[str, Any]:
        document = self._load_document(file_path)
        modelspace = document.modelspace()
        entity_count = len(modelspace)
        counts = {
            "entity_count": entity_count,
            "lines": 0,
            "lwpolylines": 0,
            "polylines": 0,
            "circles": 0,
            "arcs": 0,
            "blocks": 0,
            "texts": 0,
            "mtexts": 0,
        }

        for entity in modelspace:
            dxftype = entity.dxftype()
            if dxftype == "LINE":
                counts["lines"] += 1
            elif dxftype == "LWPOLYLINE":
                counts["lwpolylines"] += 1
            elif dxftype == "POLYLINE":
                counts["polylines"] += 1
            elif dxftype == "CIRCLE":
                counts["circles"] += 1
            elif dxftype == "ARC":
                counts["arcs"] += 1
            elif dxftype == "INSERT":
                counts["blocks"] += 1
            elif dxftype == "TEXT":
                counts["texts"] += 1
            elif dxftype == "MTEXT":
                counts["mtexts"] += 1

        return counts

    def extract_reference(self, file_path: str) -> DwgReference:
        metadata = self.extract_metadata(file_path)
        return DwgReference(
            id=Path(file_path).name,
            metadata=metadata,
            source_file=Path(file_path).name,
            extracted_features=self.extract_features(file_path),
        )

    def _load_document(self, file_path: str) -> ezdxf.document.Drawing:
        try:
            return ezdxf.readfile(file_path)
        except (ezdxf.DXFError, IOError, OSError) as exc:
            raise ValueError(f"Invalid DWG file: {file_path}") from exc
