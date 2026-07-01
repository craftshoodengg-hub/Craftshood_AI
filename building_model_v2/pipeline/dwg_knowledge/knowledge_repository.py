"""In-memory repository for DWG reference designs."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .dwg_reference import DwgReference


class KnowledgeRepository:
    """In-memory repository for storing DWG reference entries."""

    def __init__(self) -> None:
        self._references: Dict[str, DwgReference] = {}

    def add(self, reference: DwgReference) -> None:
        if reference.id in self._references:
            raise ValueError(f"Reference with id '{reference.id}' already exists.")
        self._references[reference.id] = reference

    def add_many(self, references: list[DwgReference]) -> None:
        for reference in references:
            self.add(reference)

    def remove(self, reference_id: str) -> None:
        self._references.pop(reference_id, None)

    def clear(self) -> None:
        self._references.clear()

    def count(self) -> int:
        return len(self._references)

    def all(self) -> list[DwgReference]:
        return list(self._references.values())

    def find_by_id(self, reference_id: str) -> Optional[DwgReference]:
        return self._references.get(reference_id)

    def find_by_project_type(self, project_type: str) -> list[DwgReference]:
        return [
            reference
            for reference in self._references.values()
            if reference.metadata.project_type == project_type
        ]

    def find_by_bedrooms(self, bedrooms: int) -> list[DwgReference]:
        return [
            reference
            for reference in self._references.values()
            if reference.metadata.bedrooms == bedrooms
        ]

    def find_by_floors(self, floors: int) -> list[DwgReference]:
        return [
            reference
            for reference in self._references.values()
            if reference.metadata.floors == floors
        ]

    def find_by_tag(self, tag: str) -> list[DwgReference]:
        return [
            reference
            for reference in self._references.values()
            if tag in reference.metadata.tags
        ]
