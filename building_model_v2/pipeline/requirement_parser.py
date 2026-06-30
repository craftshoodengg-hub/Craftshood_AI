"""Natural language requirement parser for design requests."""
from __future__ import annotations

import re
from typing import Iterable

from .design_request import DesignRequest


_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

_DESCRIPTOR_KEYWORDS = (
    "modern",
    "luxury",
    "minimalist",
    "traditional",
    "contemporary",
)

_COMMERCIAL_PROJECT_KEYWORDS = (
    "commercial",
    "office",
    "retail",
    "shop",
    "showroom",
    "warehouse",
)


class RequirementParser:
    """Parse free-form requirements into a structured DesignRequest."""

    @classmethod
    def parse(cls, text: str) -> DesignRequest:
        normalized = text.lower().strip()

        plot_width, plot_depth = cls._extract_plot_size(normalized)
        bedrooms = cls._extract_bedrooms(normalized)
        bathrooms = cls._extract_bathrooms(normalized)
        floors = cls._extract_floors(normalized)
        parking = cls._extract_parking(normalized)
        pooja_room = cls._contains_any(normalized, ("pooja", "puja"))
        dining_room = cls._contains_any(normalized, ("dining room", "dining area", "dining"))
        living_room = cls._extract_living_room(normalized)
        kitchen_type = cls._extract_kitchen_type(normalized)
        orientation = cls._extract_orientation(normalized)
        project_type = cls._extract_project_type(normalized)
        special_requirements = cls._extract_special_requirements(normalized)
        staircase = floors > 1 or "staircase" in normalized

        return DesignRequest(
            project_type=project_type,
            plot_width=plot_width,
            plot_depth=plot_depth,
            floors=floors,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking=parking,
            kitchen_type=kitchen_type,
            pooja_room=pooja_room,
            living_room=living_room,
            dining_room=dining_room,
            staircase=staircase,
            orientation=orientation,
            special_requirements=tuple(special_requirements),
        )

    @classmethod
    def _extract_plot_size(cls, text: str) -> tuple[float, float]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:x|×|by)\s*(\d+(?:\.\d+)?)", text)
        if not match:
            return 10.0, 10.0

        width = float(match.group(1))
        depth = float(match.group(2))
        return width, depth

    @classmethod
    def _extract_bedrooms(cls, text: str) -> int:
        match = re.search(r"(\d+|one|two|three|four|five|six)\s*(?:bhk|bedrooms?|bedroom)s?\b", text)
        if match:
            return cls._to_int(match.group(1))

        match = re.search(r"(\d+|one|two|three|four|five|six)\s*bhk\b", text)
        if match:
            return cls._to_int(match.group(1))

        return 1

    @classmethod
    def _extract_bathrooms(cls, text: str) -> int:
        match = re.search(r"(\d+|one|two|three|four|five|six)\s*(?:bathrooms?|baths?|toilets?|washrooms?|wc)s?\b", text)
        if match:
            return cls._to_int(match.group(1))
        return 1

    @classmethod
    def _extract_floors(cls, text: str) -> int:
        if re.search(r"\bg\s*\+\s*1\b|g\+1|ground\s*plus\s*one|ground\s*\+\s*one", text):
            return 2
        if re.search(r"\bduplex\b|\btwo[- ]storey\b|\btwo[- ]story\b|\btwo[- ]floor\b|\b2[- ]floor\b|\bdouble[- ]storey\b|\bdouble[- ]story\b", text):
            return 2
        match = re.search(r"(\d+|one|two|three|four|five|six)\s*(?:floors?|storeys?|stories?)\b", text)
        if match:
            return cls._to_int(match.group(1))
        if re.search(r"\bsingle\s*(?:floor|storey|story)\b|\bone\s*(?:floor|storey|story)\b", text):
            return 1
        return 1

    @classmethod
    def _extract_parking(cls, text: str) -> int:
        match = re.search(r"parking\s*(?:for\s*)?(\d+)\b", text)
        if match:
            return int(match.group(1))

        match = re.search(r"(\d+)\s*(?:cars?|parking|spaces?)\b", text)
        if match:
            return int(match.group(1))
        return 0

    @classmethod
    def _extract_living_room(cls, text: str) -> bool:
        if re.search(r"\b(no|without)\s+living\b", text):
            return False
        if cls._contains_any(text, ("living room", "living area", "living")):
            return True
        return True

    @classmethod
    def _extract_kitchen_type(cls, text: str) -> str:
        if cls._contains_any(text, ("closed kitchen", "separate kitchen", "closed-plan kitchen", "closed plan kitchen")):
            return "closed"
        if cls._contains_any(text, ("open kitchen", "open-plan kitchen", "open plan kitchen", "open concept kitchen")):
            return "open"
        return "open"

    @classmethod
    def _extract_orientation(cls, text: str) -> str:
        for orientation in ("north", "south", "east", "west"):
            if re.search(fr"\b{orientation}\b", text):
                return orientation
        return "north"

    @classmethod
    def _extract_project_type(cls, text: str) -> str:
        for keyword in _COMMERCIAL_PROJECT_KEYWORDS:
            if re.search(fr"\b{keyword}\b", text):
                return "commercial"
        return "residential"

    @classmethod
    def _extract_special_requirements(cls, text: str) -> list[str]:
        found = []
        for keyword in _DESCRIPTOR_KEYWORDS:
            if re.search(fr"\b{keyword}\b", text) and keyword not in found:
                found.append(keyword)
        return found

    @classmethod
    def _contains_any(cls, text: str, tokens: Iterable[str]) -> bool:
        return any(re.search(fr"\b{re.escape(token)}\b", text) for token in tokens)

    @classmethod
    def _to_int(cls, token: str) -> int:
        lower = token.lower().strip()
        if lower.isdigit():
            return int(lower)
        return _NUMBER_WORDS.get(lower, 0)
