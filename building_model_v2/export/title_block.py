"""Title Block for DXF Export."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
class TitleBlockData:
    project_name: str = "Craftshood AI Project"
    project_number: str = ""
    description: str = ""
    site_name: str = ""
    site_address: str = ""
    drawn_by: str = "Craftshood AI"
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    scale: str = "1:100"
    revision: str = "A"
    sheet_number: str = "1 of 1"

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name, "project_number": self.project_number,
            "description": self.description, "site_name": self.site_name,
            "site_address": self.site_address, "drawn_by": self.drawn_by,
            "date": self.date, "scale": self.scale, "revision": self.revision,
            "sheet_number": self.sheet_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TitleBlockData:
        return cls(
            project_name=data.get("project_name", "Craftshood AI Project"),
            project_number=data.get("project_number", ""),
            description=data.get("description", ""),
            site_name=data.get("site_name", ""),
            site_address=data.get("site_address", ""),
            drawn_by=data.get("drawn_by", "Craftshood AI"),
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            scale=data.get("scale", "1:100"),
            revision=data.get("revision", "A"),
            sheet_number=data.get("sheet_number", "1 of 1"),
        )
