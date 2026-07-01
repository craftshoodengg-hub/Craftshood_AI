from __future__ import annotations

from typing import Optional

from .dwg_reference import DwgReference
from .similarity_query import SimilarityQuery


class SimilarityScorer:
    """Deterministic scoring engine for DWG similarity queries."""

    @staticmethod
    def compare_area(query: SimilarityQuery, reference: DwgReference) -> Optional[float]:
        """Return percentage difference between query and reference plot area.

        The returned value is the absolute percentage difference relative to
        the reference plot area. If either side is missing, returns None.
        """
        query_area = query.area()
        reference_width = reference.metadata.plot_width
        reference_depth = reference.metadata.plot_depth
        if query_area is None or reference_width is None or reference_depth is None:
            return None

        reference_area = reference_width * reference_depth
        if reference_area == 0.0:
            return None

        return abs(query_area - reference_area) / reference_area * 100.0

    @classmethod
    def score(cls, query: SimilarityQuery, reference: DwgReference) -> float:
        """Compute a deterministic similarity score for a DWG reference."""
        score = 0.0

        if query.project_type is not None and query.project_type == reference.metadata.project_type:
            score += 0.25

        if query.bedrooms is not None and query.bedrooms == reference.metadata.bedrooms:
            score += 0.20

        if query.bathrooms is not None and query.bathrooms == reference.metadata.bathrooms:
            score += 0.10

        if query.floors is not None and query.floors == reference.metadata.floors:
            score += 0.15

        if query.orientation is not None and query.orientation == reference.metadata.orientation:
            score += 0.10

        area_difference = cls.compare_area(query, reference)
        if area_difference is not None:
            if area_difference <= 5.0:
                score += 0.20
            elif area_difference <= 10.0:
                score += 0.15
            elif area_difference <= 20.0:
                score += 0.10

        shared_tags = set(query.tags) & set(reference.metadata.tags)
        tag_score = min(len(shared_tags) * 0.02, 0.10)
        score += tag_score

        return max(0.0, min(1.0, score))
