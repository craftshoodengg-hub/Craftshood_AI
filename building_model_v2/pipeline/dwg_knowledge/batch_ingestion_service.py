"""Batch ingestion service for DWG/DXF files."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .dwg_reference import DwgReference
from .ezdxf_feature_extractor import EzDXFFeatureExtractor
from .feature_extractor import BaseFeatureExtractor
from .knowledge_repository import KnowledgeRepository


class BatchIngestionService:
    """Service that ingests DWG/DXF files into the knowledge repository."""

    def __init__(
        self,
        extractor: BaseFeatureExtractor | None = None,
        repository: KnowledgeRepository | None = None,
    ) -> None:
        self._extractor = extractor if extractor is not None else EzDXFFeatureExtractor()
        self._repository = repository if repository is not None else KnowledgeRepository()

    def ingest_directory(self, directory: str, recursive: bool = True) -> int:
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Directory does not exist: {directory}")

        candidate_files: list[Path] = []
        if recursive:
            candidate_files = [
                entry
                for entry in path.rglob("*")
                if entry.is_file() and entry.suffix.lower() in {".dwg", ".dxf"}
            ]
        else:
            candidate_files = [
                entry
                for entry in path.iterdir()
                if entry.is_file() and entry.suffix.lower() in {".dwg", ".dxf"}
            ]

        candidate_files.sort(key=lambda item: item.name)

        imported = 0
        for file_path in candidate_files:
            try:
                reference = self._extractor.extract_reference(str(file_path))
                self._repository.add(reference)
                imported += 1
            except Exception:
                continue
        return imported

    def repository(self) -> KnowledgeRepository:
        return self._repository

    def clear(self) -> None:
        self._repository.clear()

    def statistics(self) -> dict[str, Any]:
        references = self._repository.all()
        project_types: dict[str, int] = {}
        entity_counts: list[float] = []
        room_counts: list[float] = []

        for reference in references:
            project_type = reference.metadata.project_type
            project_types[project_type] = project_types.get(project_type, 0) + 1

            entity_count = reference.extracted_features.get("entity_count")
            if isinstance(entity_count, (int, float)):
                entity_counts.append(float(entity_count))

            room_count = reference.metadata.room_count
            if isinstance(room_count, (int, float)):
                room_counts.append(float(room_count))

        average_entity_count = sum(entity_counts) / len(entity_counts) if entity_counts else 0.0
        average_room_count = sum(room_counts) / len(room_counts) if room_counts else 0.0

        return {
            "files": self._repository.count(),
            "project_types": project_types,
            "average_entity_count": average_entity_count,
            "average_room_count": average_room_count,
        }
