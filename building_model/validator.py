"""Validation for aggregate building models."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .models import BuildingModel, ValidationIssue, ValidationReport


class BuildingModelValidator:
    """Validate building model consistency and completeness."""

    def validate(self, model: BuildingModel) -> ValidationReport:
        issues: list[ValidationIssue] = []
        room_ids = _ids(model.rooms, "room_id")

        if not model.metadata:
            issues.append(ValidationIssue("metadata_missing", "metadata is empty", "warning"))
        if not model.rooms:
            issues.append(ValidationIssue("rooms_missing", "at least one room is required"))
        if len(room_ids) != len(model.rooms):
            issues.append(ValidationIssue("room_id_duplicate", "room IDs must be unique"))

        self._validate_graph(
            model.adjacency_graph,
            room_ids,
            "adjacent_rooms",
            "adjacency",
            issues,
        )
        self._validate_connectivity(model.connectivity_graph, room_ids, issues)
        self._validate_room_scoped_records(model.zoning, room_ids, "zoning", issues)
        self._validate_room_scoped_records(model.confidence, room_ids, "confidence", issues)
        self._validate_facing(model.facing_information, room_ids, issues)

        return ValidationReport(
            valid=not any(issue.severity == "error" for issue in issues),
            issues=tuple(issues),
        )

    def raise_for_invalid(self, model: BuildingModel) -> None:
        report = self.validate(model)
        if not report.valid:
            messages = "; ".join(issue.message for issue in report.issues if issue.severity == "error")
            raise ValueError(messages)

    def _validate_graph(
        self,
        records: Sequence[Mapping[str, Any]],
        room_ids: set[str],
        edge_key: str,
        label: str,
        issues: list[ValidationIssue],
    ) -> None:
        for record in records:
            room_id = str(record.get("room_id", ""))
            if room_id not in room_ids:
                issues.append(
                    ValidationIssue(
                        f"{label}_unknown_room",
                        f"{label} references unknown room_id {room_id!r}",
                    )
                )
            for other_id in record.get(edge_key, ()) or ():
                if str(other_id) not in room_ids:
                    issues.append(
                        ValidationIssue(
                            f"{label}_unknown_neighbor",
                            f"{label} references unknown neighbor room_id {other_id!r}",
                        )
                    )

    def _validate_connectivity(
        self,
        records: Sequence[Mapping[str, Any]],
        room_ids: set[str],
        issues: list[ValidationIssue],
    ) -> None:
        for record in records:
            room_id = str(record.get("room_id", ""))
            if room_id not in room_ids:
                issues.append(
                    ValidationIssue(
                        "connectivity_unknown_room",
                        f"connectivity references unknown room_id {room_id!r}",
                    )
                )
            for connection in record.get("connected_rooms", ()) or ():
                other_id = str(connection.get("room_id", ""))
                if other_id not in room_ids:
                    issues.append(
                        ValidationIssue(
                            "connectivity_unknown_neighbor",
                            f"connectivity references unknown neighbor room_id {other_id!r}",
                        )
                    )

    def _validate_room_scoped_records(
        self,
        records: Sequence[Mapping[str, Any]],
        room_ids: set[str],
        label: str,
        issues: list[ValidationIssue],
    ) -> None:
        for record in records:
            room_id = str(record.get("room_id", ""))
            if room_id not in room_ids:
                issues.append(
                    ValidationIssue(
                        f"{label}_unknown_room",
                        f"{label} references unknown room_id {room_id!r}",
                    )
                )

    def _validate_facing(
        self,
        facing_information: Mapping[str, Any] | None,
        room_ids: set[str],
        issues: list[ValidationIssue],
    ) -> None:
        if not facing_information:
            issues.append(ValidationIssue("facing_missing", "facing information is missing", "warning"))
            return
        for room_id in facing_information.get("front_rooms", ()) or ():
            if str(room_id) not in room_ids:
                issues.append(
                    ValidationIssue(
                        "facing_unknown_front_room",
                        f"facing references unknown front room_id {room_id!r}",
                    )
                )


def _ids(records: Sequence[Mapping[str, Any]], key: str) -> set[str]:
    return {str(record.get(key, "")) for record in records if record.get(key)}
