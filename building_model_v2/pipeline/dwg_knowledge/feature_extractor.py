"""DWG feature extractor abstraction for the knowledge base."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .dwg_metadata import DwgMetadata
from .dwg_reference import DwgReference


class BaseFeatureExtractor(ABC):
    """Abstract base for DWG feature extractors."""

    @abstractmethod
    def extract_metadata(self, file_path: str) -> DwgMetadata:
        """Extract DWG metadata from a drawing file."""
        raise NotImplementedError

    @abstractmethod
    def extract_reference(self, file_path: str) -> DwgReference:
        """Extract a reference design entry from a drawing file."""
        raise NotImplementedError

    @abstractmethod
    def extract_features(self, file_path: str) -> dict[str, Any]:
        """Extract raw architectural features from a drawing file."""
        raise NotImplementedError


class DummyFeatureExtractor(BaseFeatureExtractor):
    """Dummy DWG feature extractor used for deterministic tests."""

    def extract_metadata(self, file_path: str) -> DwgMetadata:
        project_type = "residential" if "residential" in file_path else "commercial"
        return DwgMetadata(
            file_path=file_path,
            project_type=project_type,
            plot_width=20.0,
            plot_depth=30.0,
            floors=1,
            bedrooms=3,
            bathrooms=2,
            room_count=7,
            total_area=1800.0,
            orientation="north",
            tags=["dummy", "test", project_type],
        )

    def extract_features(self, file_path: str) -> dict[str, Any]:
        return {
            "file_path": file_path,
            "room_count": 7,
            "has_parking": True,
            "main_orientation": "north",
            "zones": ["living", "kitchen", "bedroom", "bathroom"],
        }

    def extract_reference(self, file_path: str) -> DwgReference:
        metadata = self.extract_metadata(file_path)
        return DwgReference(
            id=f"dummy-{file_path}",
            metadata=metadata,
            source_file=file_path,
            extracted_features=self.extract_features(file_path),
        )
