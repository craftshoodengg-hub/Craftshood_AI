"""DWG knowledge base domain package."""
from __future__ import annotations

from .dwg_metadata import DwgMetadata
from .dwg_reference import DwgReference
from .architectural_feature_extractor import ArchitecturalFeatureExtractor
from .dataset_analyzer import DatasetAnalyzer
from .dataset_report_exporter import DatasetReportExporter
from .ezdxf_feature_extractor import EzDXFFeatureExtractor
from .feature_extractor import BaseFeatureExtractor, DummyFeatureExtractor
from .knowledge_repository import KnowledgeRepository
from .similarity_query import SimilarityQuery, SimilarityResult
from .similarity_scorer import SimilarityScorer
from .retrieval_engine import RetrievalEngine
from .retrieval_service import RetrievalService
from .batch_ingestion_service import BatchIngestionService
from .dwg_conversion_guide import (
    recommended_converted_folder,
    conversion_instructions,
    validate_converted_folder,
)
from .room_label_detector import RoomLabelDetector, normalize_label
from .room_polygon_builder import RoomPolygonBuilder
from .room_opening_assigner import RoomOpeningAssigner
from .plot_information_detector import PlotInformationDetector
from .door_window_detector import DoorWindowDetector

__all__ = [
    "DwgMetadata",
    "DwgReference",
    "ArchitecturalFeatureExtractor",
    "DatasetAnalyzer",
    "DatasetReportExporter",
    "EzDXFFeatureExtractor",
    "BaseFeatureExtractor",
    "DummyFeatureExtractor",
    "KnowledgeRepository",
    "SimilarityQuery",
    "SimilarityResult",
    "SimilarityScorer",
    "RetrievalEngine",
    "RetrievalService",
    "BatchIngestionService",
    "recommended_converted_folder",
    "conversion_instructions",
    "validate_converted_folder",
    "RoomLabelDetector",
    "normalize_label",
    "RoomPolygonBuilder",
    "RoomOpeningAssigner",
    "PlotInformationDetector",
    "DoorWindowDetector",
]
