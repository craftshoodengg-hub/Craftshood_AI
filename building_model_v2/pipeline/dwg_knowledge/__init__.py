"""DWG knowledge base domain package."""
from __future__ import annotations

from .dwg_metadata import DwgMetadata
from .dwg_reference import DwgReference
from .feature_extractor import BaseFeatureExtractor, DummyFeatureExtractor
from .knowledge_repository import KnowledgeRepository
from .similarity_query import SimilarityQuery, SimilarityResult
from .similarity_scorer import SimilarityScorer
from .retrieval_engine import RetrievalEngine
from .retrieval_service import RetrievalService

__all__ = [
    "DwgMetadata",
    "DwgReference",
    "BaseFeatureExtractor",
    "DummyFeatureExtractor",
    "KnowledgeRepository",
    "SimilarityQuery",
    "SimilarityResult",
    "SimilarityScorer",
    "RetrievalEngine",
    "RetrievalService",
]
