"""Deterministic design advisor rule implementations."""
from __future__ import annotations

from typing import Any

from .advisor_rule import BaseAdvisorRule
from .advice_result import AdviceResult
from .design_advice import DesignAdvice
from ..design_request import DesignRequest


class BasicAdvisorRule(BaseAdvisorRule):
    """Basic deterministic advisor rule for design guidance."""

    @property
    def name(self) -> str:
        return "basic-advisor"

    def analyze(
        self,
        design_request: DesignRequest | None,
        building_model: Any = None,
        pipeline_result: Any = None,
    ) -> AdviceResult:
        result = AdviceResult()
        if design_request is None:
            return result

        advice: list[DesignAdvice] = []
        strengths: list[str] = []
        weaknesses: list[str] = []

        plot_area = design_request.area()
        if plot_area >= 1200:
            strengths.append("Large plot provides excellent design flexibility.")
            advice.append(
                DesignAdvice(
                    category="plot",
                    title="Large plot",
                    description="The plot is large enough to support flexible architectural planning.",
                    severity="info",
                    recommendation="Use the generous plot area to organize functional zones clearly.",
                )
            )
        elif plot_area < 600:
            weaknesses.append("Small plot limits planning flexibility.")
            advice.append(
                DesignAdvice(
                    category="plot",
                    title="Small plot",
                    description="The plot area is constrained and may limit layout flexibility.",
                    severity="warning",
                    recommendation="Prioritize compact planning and multi-functional spaces.",
                )
            )

        if design_request.bedrooms >= 3:
            strengths.append("Suitable for medium to large families.")
            advice.append(
                DesignAdvice(
                    category="bedroom",
                    title="Family-friendly bedroom count",
                    description="The requested bedroom count supports larger family living.",
                    severity="info",
                    recommendation="Keep bedroom adjacencies efficient for family use.",
                )
            )
        elif design_request.bedrooms == 1:
            advice.append(
                DesignAdvice(
                    category="bedroom",
                    title="Limited bedroom count",
                    description="A single bedroom request may constrain future expansion.",
                    severity="recommendation",
                    recommendation="Consider allocating space for future bedroom expansion.",
                )
            )

        if design_request.parking > 0:
            strengths.append("Dedicated parking improves convenience.")
            advice.append(
                DesignAdvice(
                    category="parking",
                    title="Parking provision",
                    description="A parking provision has been requested.",
                    severity="info",
                    recommendation="Plan the parking layout for easy access to the entrance.",
                )
            )

        if not design_request.living_room:
            weaknesses.append("Living room not requested.")
            advice.append(
                DesignAdvice(
                    category="living_room",
                    title="Living room absent",
                    description="No living room has been requested.",
                    severity="warning",
                    recommendation="Evaluate whether a living room should be included for social spaces.",
                )
            )

        if not design_request.pooja_room:
            advice.append(
                DesignAdvice(
                    category="pooja_room",
                    title="Pooja room not requested",
                    description="A pooja room is not part of the current request.",
                    severity="recommendation",
                    recommendation="Consider including a pooja room if cultural requirements apply.",
                )
            )

        if design_request.floors > 2:
            weaknesses.append("Multi-storey designs require careful structural planning.")
            advice.append(
                DesignAdvice(
                    category="floors",
                    title="Multi-storey design",
                    description="More than two floors increases structural and circulation complexity.",
                    severity="warning",
                    recommendation="Ensure structural and vertical circulation requirements are addressed.",
                )
            )

        warning_count = sum(1 for item in advice if item.severity == "warning")
        recommendation_count = sum(1 for item in advice if item.severity == "recommendation")
        score = 100 - warning_count * 5 - recommendation_count * 3
        score = max(0.0, min(100.0, float(score)))

        return AdviceResult(
            advice=advice,
            score=score,
            strengths=strengths,
            weaknesses=weaknesses,
        )
