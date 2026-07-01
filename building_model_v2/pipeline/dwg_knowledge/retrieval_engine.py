from __future__ import annotations

from typing import List, Optional

from .dwg_reference import DwgReference
from .knowledge_repository import KnowledgeRepository
from .similarity_query import SimilarityQuery
from .similarity_scorer import SimilarityScorer
from .similarity_query import SimilarityResult


class RetrievalEngine:
    """Retrieval engine for DWG references using deterministic similarity scoring."""

    def __init__(
        self,
        repository: KnowledgeRepository,
        scorer: SimilarityScorer | None = None,
    ) -> None:
        self.repository = repository
        self.scorer = scorer if scorer is not None else SimilarityScorer()

    def retrieve(self, query: SimilarityQuery) -> list[SimilarityResult]:
        results: List[SimilarityResult] = []
        for reference in self.repository.all():
            score = self.scorer.score(query, reference)
            if score <= 0.0:
                continue
            results.append(SimilarityResult(reference=reference, score=score))

        results.sort(key=lambda result: result.score, reverse=True)
        return results[: query.max_results]

    def best_match(self, query: SimilarityQuery) -> Optional[SimilarityResult]:
        matches = self.retrieve(query)
        return matches[0] if matches else None

    def top_matches(self, query: SimilarityQuery, limit: int) -> list[SimilarityResult]:
        if limit < 0:
            raise ValueError("limit must be non-negative")
        results = self.retrieve(query)
        return results[:limit]
