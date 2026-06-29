"""Report metadata for PDF reports."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self


@dataclass(frozen=True, slots=True)
class ReportMetadata:
    """Metadata for a PDF report."""
    project_name: str = 'Untitled Project'
    report_version: str = '1.0.0'
    engine_version: str = '2.0.0'
    craftshood_version: str = '2.0.0'
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    generated_by: str = 'Craftshood AI'
    revision: str = 'A'
    author: str = ''
    organization: str = ''
    description: str = ''
    def to_dict(self):
        return {
            'project_name': self.project_name, 'report_version': self.report_version,
            'engine_version': self.engine_version, 'craftshood_version': self.craftshood_version,
            'generated_at': self.generated_at, 'generated_by': self.generated_by,
            'revision': self.revision, 'author': self.author,
            'organization': self.organization, 'description': self.description,
        }

    @classmethod
    def from_dict(cls, payload):
        return cls(
            project_name=str(payload.get('project_name', 'Untitled Project')),
            report_version=str(payload.get('report_version', '1.0.0')),
            engine_version=str(payload.get('engine_version', '2.0.0')),
            craftshood_version=str(payload.get('craftshood_version', '2.0.0')),
            generated_at=str(payload.get('generated_at', datetime.now(timezone.utc).isoformat())),
            generated_by=str(payload.get('generated_by', 'Craftshood AI')),
            revision=str(payload.get('revision', 'A')),
            author=str(payload.get('author', '')),
            organization=str(payload.get('organization', '')),
            description=str(payload.get('description', '')),
        )

    @classmethod
    def create(cls, project_name='Untitled Project', **kwargs):
        return cls(project_name=project_name, **kwargs)
