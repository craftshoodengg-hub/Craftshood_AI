"""DWG knowledge base reference model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .dwg_metadata import DwgMetadata


@dataclass(frozen=True, slots=True)
class DwgReference:
    """A reference DWG design entry for the knowledge base."""

    id: str
    metadata: DwgMetadata
    source_file: str
    extracted_features: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "metadata": self.metadata.to_dict(),
            "source_file": self.source_file,
            "extracted_features": dict(self.extracted_features),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DwgReference":
        return cls(
            id=str(data["id"]),
            metadata=DwgMetadata.from_dict(data["metadata"]),
            source_file=str(data["source_file"]),
            extracted_features=dict(data.get("extracted_features", {})),
        )
