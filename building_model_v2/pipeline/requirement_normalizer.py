"""Normalize and validate design requests before pipeline execution."""
from __future__ import annotations

from typing import Iterable

from .design_request import DesignRequest


_PROJECT_TYPE_MAP = {
    "apartment": "residential",
    "villa": "residential",
    "bungalow": "residential",
    "office": "commercial",
    "shop": "commercial",
}

_KITCHEN_TYPE_MAP = {
    "open kitchen": "open",
    "modular kitchen": "modular",
    "closed kitchen": "closed",
    "closed-plan kitchen": "closed",
    "open-plan kitchen": "open",
}

_ORIENTATION_VALUES = ("north", "south", "east", "west")

_FLOOR_SYNONYMS = {
    "duplex": 2,
    "g+1": 2,
    "g+2": 3,
}

_PARKING_KEYWORDS = (
    "garage",
    "car porch",
    "carport",
    "covered parking",
)


class RequirementNormalizer:
    """Normalize and validate a DesignRequest before pipeline execution."""

    @classmethod
    def normalize(cls, request: DesignRequest) -> DesignRequest:
        project_type = cls._normalize_project_type(request.project_type, request.special_requirements)
        kitchen_type = cls._normalize_kitchen_type(request.kitchen_type, request.special_requirements)
        orientation = cls._normalize_orientation(request.orientation)
        floors = cls._normalize_floors(request.floors, request.project_type, request.special_requirements)
        bathrooms = cls._normalize_bathrooms(request.bathrooms, request.bedrooms)
        parking = cls._normalize_parking(request.parking, request.project_type, request.special_requirements)

        cls._validate_fields(
            request.plot_width,
            request.plot_depth,
            request.bedrooms,
            bathrooms,
            floors,
        )

        normalized_request = DesignRequest(
            project_type=project_type,
            plot_width=request.plot_width,
            plot_depth=request.plot_depth,
            floors=floors,
            bedrooms=request.bedrooms,
            bathrooms=bathrooms,
            parking=parking,
            kitchen_type=kitchen_type,
            pooja_room=request.pooja_room,
            living_room=request.living_room,
            dining_room=request.dining_room,
            staircase=request.staircase,
            orientation=orientation,
            special_requirements=request.special_requirements,
        )

        return normalized_request

    @classmethod
    def _normalize_project_type(cls, project_type: str, special_requirements: Iterable[str]) -> str:
        normalized = project_type.strip().lower()
        if normalized in _PROJECT_TYPE_MAP:
            return _PROJECT_TYPE_MAP[normalized]

        for keyword, mapped in _PROJECT_TYPE_MAP.items():
            if keyword in normalized:
                return mapped

        for requirement in special_requirements:
            if requirement.lower() in _PROJECT_TYPE_MAP:
                return _PROJECT_TYPE_MAP[requirement.lower()]

        return normalized

    @classmethod
    def _normalize_kitchen_type(cls, kitchen_type: str, special_requirements: Iterable[str]) -> str:
        normalized = kitchen_type.strip().lower()
        for keyword, mapped in _KITCHEN_TYPE_MAP.items():
            if keyword in normalized:
                return mapped

        for requirement in special_requirements:
            key = requirement.lower()
            for keyword, mapped in _KITCHEN_TYPE_MAP.items():
                if keyword in key:
                    return mapped

        return normalized

    @classmethod
    def _normalize_orientation(cls, orientation: str) -> str:
        normalized = orientation.strip().lower()
        for value in _ORIENTATION_VALUES:
            if value == normalized or value in normalized:
                return value
        return "north"

    @classmethod
    def _normalize_floors(
        cls,
        floors: int,
        project_type: str,
        special_requirements: Iterable[str],
    ) -> int:
        normalized = project_type.strip().lower()
        if normalized in _FLOOR_SYNONYMS:
            return _FLOOR_SYNONYMS[normalized]

        for requirement in special_requirements:
            keyword = requirement.lower()
            if keyword in _FLOOR_SYNONYMS:
                return _FLOOR_SYNONYMS[keyword]

        return floors

    @classmethod
    def _normalize_bathrooms(cls, bathrooms: int, bedrooms: int) -> int:
        if bathrooms == 0:
            return max(1, bedrooms)
        return bathrooms

    @classmethod
    def _normalize_parking(
        cls,
        parking: int,
        project_type: str,
        special_requirements: Iterable[str],
    ) -> int:
        if parking > 0:
            return parking

        if cls._matches_parking_keyword(project_type):
            return 1

        for requirement in special_requirements:
            if cls._matches_parking_keyword(requirement):
                return 1

        return 0

    @classmethod
    def _matches_parking_keyword(cls, text: str) -> bool:
        normalized = text.strip().lower()
        return any(keyword in normalized for keyword in _PARKING_KEYWORDS)

    @classmethod
    def _validate_fields(
        cls,
        plot_width: float,
        plot_depth: float,
        bedrooms: int,
        bathrooms: int,
        floors: int,
    ) -> None:
        if plot_width <= 0 or plot_depth <= 0:
            raise ValueError("plot dimensions must be greater than 0")
        if bedrooms > 20:
            raise ValueError("bedrooms must be 20 or fewer")
        if bathrooms > bedrooms + 3:
            raise ValueError("bathrooms must be at most bedrooms + 3")
        if floors > 10:
            raise ValueError("floors must be 10 or fewer")
