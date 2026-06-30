"""Basic deterministic Vastu rule implementation."""
from __future__ import annotations

from .vastu_result import VastuResult
from .vastu_rule import BaseVastuRule
from ..design_request import DesignRequest


class BasicVastuRule(BaseVastuRule):
    """Simple Vastu advisory rule for basic guidance."""

    @property
    def name(self) -> str:
        return "BasicVastuRule"

    def analyze(self, design_request: DesignRequest) -> VastuResult:
        score = 0.0
        warnings: list[str] = []
        suggestions: list[str] = []

        # Entrance orientation guidance.
        orientation = design_request.orientation.strip().lower()
        if orientation in {"north", "east"}:
            score += 20.0
        elif orientation in {"south", "west"}:
            score += 10.0
        else:
            warnings.append("Entrance orientation is unknown; Vastu guidance may be limited.")

        # Kitchen guidance.
        kitchen_type = design_request.kitchen_type.strip().lower()
        if kitchen_type == "open":
            score += 10.0
        elif kitchen_type == "modular":
            score += 8.0
        elif kitchen_type == "closed":
            score += 5.0
        else:
            warnings.append("Kitchen type is unspecified; Vastu score may be incomplete.")

        # Pooja room guidance.
        if design_request.pooja_room:
            score += 15.0
        else:
            suggestions.append("Consider adding a pooja room for better Vastu balance.")

        # Bedroom guidance.
        if design_request.bedrooms >= 3 and not design_request.pooja_room:
            suggestions.append(
                "With three or more bedrooms, a dedicated pooja room is recommended."
            )

        # Parking guidance.
        if design_request.parking > 0:
            score += 5.0

        # Floor guidance.
        if design_request.floors > 2:
            warnings.append("More than two floors may require additional Vastu consideration.")

        score = max(0.0, min(score, 100.0))

        return VastuResult(
            passed=True,
            score=score,
            warnings=warnings,
            suggestions=suggestions,
            rule_name=self.name,
        )
