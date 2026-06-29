"""Unit tests for Building entity."""

from __future__ import annotations

import pytest

from building_model_v2 import Building


class TestBuilding:
    """Tests for Building entity."""
    
    def test_create_with_defaults(self) -> None:
        building = Building()
        assert building.name == ""
        assert building.project_number == ""
        assert building.description == ""
        assert building.site_name == ""
        assert building.site_address == ""
        assert building.north_direction == pytest.approx(0.0)
        assert building.units == "imperial"
        assert building.floor_ids == ()
    
    def test_create_with_values(self) -> None:
        building = Building(
            name="My House",
            project_number="PRJ-001",
            description="A residential building",
            site_name="Sunset Villa",
            site_address="123 Main St, City, State",
            north_direction=45.0,
            units="metric",
        )
        assert building.name == "My House"
        assert building.project_number == "PRJ-001"
        assert building.description == "A residential building"
        assert building.site_name == "Sunset Villa"
        assert building.site_address == "123 Main St, City, State"
        assert building.north_direction == pytest.approx(45.0)
        assert building.units == "metric"
    
    def test_create_factory(self) -> None:
        building = Building.create(
            name="Office Building",
            project_number="PRJ-002",
            description="Commercial office space",
            site_name="Downtown Tower",
            site_address="456 Business Ave, City, State",
            north_direction=180.0,
            units="imperial",
            floor_ids=("floor-1", "floor-2", "floor-3"),
        )
        assert building.name == "Office Building"
        assert building.project_number == "PRJ-002"
        assert building.floor_ids == ("floor-1", "floor-2", "floor-3")
    
    def test_create_factory_with_floors(self) -> None:
        building = Building.create(
            name="Multi-Story",
            floor_ids=("floor-b1", "floor-1", "floor-2", "floor-3"),
        )
        assert building.floor_count == 4
        assert building.has_multiple_floors is True
    
    def test_floor_count_empty(self) -> None:
        building = Building()
        assert building.floor_count == 0
    
    def test_floor_count_single(self) -> None:
        building = Building(floor_ids=("floor-1",))
        assert building.floor_count == 1
    
    def test_floor_count_multiple(self) -> None:
        building = Building(floor_ids=("floor-1", "floor-2", "floor-3"))
        assert building.floor_count == 3
    
    def test_has_multiple_floors_true(self) -> None:
        building = Building(floor_ids=("floor-1", "floor-2"))
        assert building.has_multiple_floors is True
    
    def test_has_multiple_floors_false_single(self) -> None:
        building = Building(floor_ids=("floor-1",))
        assert building.has_multiple_floors is False
    
    def test_has_multiple_floors_false_empty(self) -> None:
        building = Building()
        assert building.has_multiple_floors is False
    
    def test_is_single_floor_true(self) -> None:
        building = Building(floor_ids=("floor-1",))
        assert building.is_single_floor is True
    
    def test_is_single_floor_false(self) -> None:
        building = Building(floor_ids=("floor-1", "floor-2"))
        assert building.is_single_floor is False
    
    def test_is_empty_true(self) -> None:
        building = Building()
        assert building.is_empty is True
    
    def test_is_empty_false(self) -> None:
        building = Building(floor_ids=("floor-1",))
        assert building.is_empty is False
    
    def test_ground_floor_id_with_floors(self) -> None:
        building = Building(floor_ids=("floor-1", "floor-2", "floor-3"))
        assert building.ground_floor_id == "floor-1"
    
    def test_ground_floor_id_empty(self) -> None:
        building = Building()
        assert building.ground_floor_id is None
    
    def test_top_floor_id_with_floors(self) -> None:
        building = Building(floor_ids=("floor-1", "floor-2", "floor-3"))
        assert building.top_floor_id == "floor-3"
    
    def test_top_floor_id_empty(self) -> None:
        building = Building()
        assert building.top_floor_id is None
    
    def test_has_metric_units_true(self) -> None:
        building = Building(units="metric")
        assert building.has_metric_units is True
    
    def test_has_metric_units_false(self) -> None:
        building = Building(units="imperial")
        assert building.has_metric_units is False
    
    def test_has_imperial_units_true(self) -> None:
        building = Building(units="imperial")
        assert building.has_imperial_units is True
    
    def test_has_imperial_units_false(self) -> None:
        building = Building(units="metric")
        assert building.has_imperial_units is False
    
    def test_to_dict(self) -> None:
        building = Building.create(
            name="Test Building",
            project_number="PRJ-TEST",
            description="A test building",
            site_name="Test Site",
            site_address="Test Address",
            north_direction=90.0,
            units="metric",
            floor_ids=("floor-1", "floor-2"),
        )
        result = building.to_dict()
        assert result["name"] == "Test Building"
        assert result["project_number"] == "PRJ-TEST"
        assert result["description"] == "A test building"
        assert result["site_name"] == "Test Site"
        assert result["site_address"] == "Test Address"
        assert result["north_direction"] == pytest.approx(90.0)
        assert result["units"] == "metric"
        assert result["floor_ids"] == ["floor-1", "floor-2"]
        assert result["computed"]["floor_count"] == 2
        assert result["computed"]["has_multiple_floors"] is True
        assert result["computed"]["ground_floor_id"] == "floor-1"
        assert result["computed"]["top_floor_id"] == "floor-2"
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "building-1",
            "name": "My Building",
            "project_number": "PRJ-001",
            "description": "Description",
            "site_name": "Site Name",
            "site_address": "Site Address",
            "north_direction": 270.0,
            "units": "imperial",
            "floor_ids": ["floor-1", "floor-2", "floor-3"],
        }
        building = Building.from_dict(payload)
        assert building.id == "building-1"
        assert building.name == "My Building"
        assert building.project_number == "PRJ-001"
        assert building.description == "Description"
        assert building.site_name == "Site Name"
        assert building.site_address == "Site Address"
        assert building.north_direction == pytest.approx(270.0)
        assert building.units == "imperial"
        assert building.floor_ids == ("floor-1", "floor-2", "floor-3")
    
    def test_from_dict_defaults(self) -> None:
        building = Building.from_dict({})
        assert building.name == ""
        assert building.units == "imperial"
        assert building.floor_ids == ()
    
    def test_from_dict_partial(self) -> None:
        payload = {
            "id": "building-2",
            "name": "Partial Building",
        }
        building = Building.from_dict(payload)
        assert building.id == "building-2"
        assert building.name == "Partial Building"
        assert building.north_direction == pytest.approx(0.0)
    
    def test_immutability(self) -> None:
        building = Building()
        with pytest.raises(AttributeError):
            building.name = "New Name"  # type: ignore
    
    def test_immutability_units(self) -> None:
        building = Building()
        with pytest.raises(AttributeError):
            building.units = "metric"  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        building = Building()
        assert hasattr(building, "id")
        assert hasattr(building, "created_at")
        assert hasattr(building, "updated_at")
        assert hasattr(building, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Building.create(
            name="Round Trip Building",
            project_number="PRJ-RT",
            description="Testing round trip",
            site_name="RT Site",
            site_address="RT Address",
            north_direction=135.0,
            units="metric",
            floor_ids=("f1", "f2", "f3"),
            metadata={"type": "residential"},
        )
        data = original.to_dict()
        restored = Building.from_dict(data)
        assert restored.name == original.name
        assert restored.project_number == original.project_number
        assert restored.description == original.description
        assert restored.site_name == original.site_name
        assert restored.site_address == original.site_address
        assert restored.north_direction == original.north_direction
        assert restored.units == original.units
        assert restored.floor_ids == original.floor_ids
        assert restored.metadata == original.metadata
    
    def test_equality(self) -> None:
        building1 = Building(name="Building A")
        building2 = Building(name="Building A")
        # Different IDs by default
        assert building1 != building2
    
    def test_equality_same_id(self) -> None:
        building1 = Building(
            id="same-id",
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
            name="Building A",
        )
        building2 = Building(
            id="same-id",
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
            name="Building A",
        )
        assert building1 == building2
    
    def test_north_direction_zero(self) -> None:
        building = Building(north_direction=0.0)
        assert building.north_direction == pytest.approx(0.0)
    
    def test_north_direction_full_circle(self) -> None:
        building = Building(north_direction=360.0)
        assert building.north_direction == pytest.approx(360.0)
    
    def test_empty_strings(self) -> None:
        building = Building(
            name="",
            project_number="",
            description="",
            site_name="",
            site_address="",
        )
        assert building.name == ""
        assert building.project_number == ""
        assert building.description == ""
        assert building.site_name == ""
        assert building.site_address == ""
    
    def test_metadata_preserved(self) -> None:
        building = Building(
            name="Test",
            metadata={"architect": "John Doe", "year": 2024}
        )
        assert building.metadata["architect"] == "John Doe"
        assert building.metadata["year"] == 2024
    
    def test_many_floors(self) -> None:
        floor_ids = tuple(f"floor-{i}" for i in range(20))
        building = Building(floor_ids=floor_ids)
        assert building.floor_count == 20
        assert building.has_multiple_floors is True
        assert building.ground_floor_id == "floor-0"
        assert building.top_floor_id == "floor-19"
    
    def test_floor_ids_tuple_immutable(self) -> None:
        building = Building(floor_ids=("floor-1", "floor-2"))
        with pytest.raises(AttributeError):
            building.floor_ids = ("floor-3",)  # type: ignore
    
    def test_to_dict_includes_base_fields(self) -> None:
        building = Building(name="Test")
        result = building.to_dict()
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "metadata" in result
    
    def test_from_dict_preserves_timestamps(self) -> None:
        payload = {
            "id": "building-1",
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-02T00:00:00+00:00",
        }
        building = Building.from_dict(payload)
        assert building.id == "building-1"
        assert building.created_at == "2024-01-01T00:00:00+00:00"
        assert building.updated_at == "2024-01-02T00:00:00+00:00"
    
    def test_from_dict_generates_timestamps_if_missing(self) -> None:
        building = Building.from_dict({"id": "building-1"})
        assert building.created_at is not None
        assert building.updated_at is not None
    
    def test_building_with_all_properties(self) -> None:
        building = Building(
            name="Complete Building",
            project_number="PRJ-COMPLETE",
            description="A fully specified building",
            site_name="Complete Site",
            site_address="789 Complete Ave, City, State",
            north_direction=225.5,
            units="metric",
            floor_ids=("basement", "ground", "first", "second", "roof"),
            metadata={
                "architect": "Jane Smith",
                "year_built": 2023,
                "total_area": 50000,
                "type": "commercial",
            },
        )
        assert building.name == "Complete Building"
        assert building.floor_count == 5
        assert building.has_multiple_floors is True
        assert building.ground_floor_id == "basement"
        assert building.top_floor_id == "roof"
        assert building.has_metric_units is True
        assert building.metadata["architect"] == "Jane Smith"
    
    def test_negative_north_direction(self) -> None:
        building = Building(north_direction=-45.0)
        assert building.north_direction == pytest.approx(-45.0)
    
    def test_large_north_direction(self) -> None:
        building = Building(north_direction=720.0)
        assert building.north_direction == pytest.approx(720.0)
    
    def test_default_units_is_imperial(self) -> None:
        building = Building()
        assert building.units == "imperial"
        assert building.has_imperial_units is True
        assert building.has_metric_units is False
    
    def test_empty_floor_ids_tuple(self) -> None:
        building = Building(floor_ids=())
        assert building.floor_ids == ()
        assert building.floor_count == 0
        assert building.is_empty is True