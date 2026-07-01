from __future__ import annotations

from typing import Iterable

from .dwg_reference import DwgReference
from .knowledge_repository import KnowledgeRepository
from .retrieval_engine import RetrievalEngine
from .similarity_query import SimilarityQuery, SimilarityResult
from .similarity_scorer import SimilarityScorer


class RetrievalService:
    """High-level service for managing DWG knowledge retrieval."""

    def __init__(self, repository: KnowledgeRepository | None = None) -> None:
        self._repository = repository if repository is not None else KnowledgeRepository()
        self._scorer = SimilarityScorer()
        self._engine = RetrievalEngine(self._repository, scorer=self._scorer)

    def repository(self) -> KnowledgeRepository:
        return self._repository

    def add_reference(self, reference: DwgReference) -> None:
        self._repository.add(reference)

    def add_references(self, references: Iterable[DwgReference]) -> None:
        self._repository.add_many(list(references))

    def clear(self) -> None:
        self._repository.clear()

    def count(self) -> int:
        return self._repository.count()

    def retrieve(self, query: SimilarityQuery) -> list[SimilarityResult]:
        return self._engine.retrieve(query)

    def best_match(self, query: SimilarityQuery) -> SimilarityResult | None:
        return self._engine.best_match(query)

    def top_matches(self, query: SimilarityQuery, limit: int) -> list[SimilarityResult]:
        return self._engine.top_matches(query, limit)
