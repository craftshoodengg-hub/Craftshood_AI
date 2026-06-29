"""Layout Evaluation Result for Building Model v2."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

from .circulation_metrics import CirculationMetrics
from .egress_metrics import EgressMetrics
from .privacy_metrics import PrivacyMetrics


@dataclass(frozen=True, slots=True)
class LayoutEvaluationResult:
    adjacency_result: "ConstraintResult"
    circulation_metrics: CirculationMetrics
    circulation_result: "ConstraintResult"
    privacy_metrics: PrivacyMetrics
    egress_metrics: EgressMetrics
    egress_result: "ConstraintResult"

    @property
    def overall_layout_score(self) -> float:
        score = 100.0
        score -= self.adjacency_result.issue_count * 2.0
        score -= len(self.privacy_metrics.privacy_conflicts) * 3.0
        score -= self.egress_result.issue_count * 4.0
        score -= self.circulation_result.issue_count * 2.0
        return max(0.0, min(100.0, score))

    @property
    def issue_count(self) -> int:
        return (self.adjacency_result.issue_count +
                len(self.privacy_metrics.privacy_conflicts) +
                self.egress_result.issue_count +
                self.circulation_result.issue_count)

    @property
    def warning_count(self) -> int:
        from ..constraints.constraint_severity import ConstraintSeverity
        count = sum(1 for i in self.adjacency_result.issues if i.severity == ConstraintSeverity.WARNING)
        count += sum(1 for i in self.egress_result.issues if i.severity == ConstraintSeverity.WARNING)
        count += sum(1 for i in self.circulation_result.issues if i.severity == ConstraintSeverity.WARNING)
        count += len(self.privacy_metrics.privacy_conflicts)
        return count

    @property
    def recommendation_count(self) -> int:
        from ..constraints.constraint_severity import ConstraintSeverity
        count = sum(1 for i in self.adjacency_result.issues if i.severity == ConstraintSeverity.RECOMMENDATION)
        count += sum(1 for i in self.egress_result.issues if i.severity == ConstraintSeverity.RECOMMENDATION)
        count += sum(1 for i in self.circulation_result.issues if i.severity == ConstraintSeverity.RECOMMENDATION)
        return count

    @property
    def layout_quality(self) -> str:
        score = self.overall_layout_score
        if score >= 95:
            return "Excellent"
        elif score >= 85:
            return "Good"
        elif score >= 70:
            return "Fair"
        else:
            return "Poor"

    def to_dict(self) -> Dict[str, Any]:
        return {"overall_layout_score": self.overall_layout_score, "issue_count": self.issue_count, "warning_count": self.warning_count, "recommendation_count": self.recommendation_count, "layout_quality": self.layout_quality, "adjacency_issues": self.adjacency_result.issue_count, "privacy_conflicts": len(self.privacy_metrics.privacy_conflicts), "egress_issues": self.egress_result.issue_count, "circulation_issues": self.circulation_result.issue_count, "circulation_efficiency": self.circulation_metrics.circulation_efficiency, "egress_score": self.egress_metrics.egress_score, "privacy_score": self.privacy_metrics.privacy_score}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LayoutEvaluationResult":
        raise NotImplementedError("Deserialization not supported for aggregated result")
