"""DWG knowledge base domain package."""
from __future__ import annotations

from .dwg_metadata import DwgMetadata
from .dwg_reference import DwgReference
from .feature_extractor import BaseFeatureExtractor, DummyFeatureExtractor
from .knowledge_repository import KnowledgeRepository

__all__ = [
    "DwgMetadata",
    "DwgReference",
    "BaseFeatureExtractor",
    "DummyFeatureExtractor",
    "KnowledgeRepository",
]
