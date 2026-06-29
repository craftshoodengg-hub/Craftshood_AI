"""Unit tests for Space Program."""
from __future__ import annotations
import pytest
from building_model_v2.ai.room_program import (
    FloorPreference,
    PrivacyLevel,
    RoomProgram,
)
from building_model_v2.ai.space_program import SpaceProgram
from building_model_v2.ai.space_generator import (
    DEFAULT_ROOM_AREAS,
    MAXIMUM_AREA_FACTOR,
    MINIMUM_AREA_FACTOR,
    ROOM_ADJACENCY_PREFERENCES,
    ROOM_ADJACENCY_REQUIREMENTS,
    ROOM_CIRCULATION,
    ROOM_FLOOR_PREFERENCE,
    ROOM_NATURAL_LIGHT,
    ROOM_PRIVACY,
    ROOM_VASTU,
    ROOM_VENTILATION,
    SpaceProgramGenerator,
)
from building_model_v2.ai.design_requirements import (
    BuildingRequirements,
    DesignRequirements,
    PlotRequirements,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def generator() -> SpaceProgramGenerator:
    return SpaceProgramGenerator()


@pytest.fixture
def req_3bhk() -> DesignRequirements:
    return DesignRequirements(
        plot=PlotRequirements(width=40.0, length=60.0, facing="east"),
        building=BuildingRequirements(
            building_type="duplex",
            floors=2,
            bedrooms=3,
            bathrooms=2,
            parking=True,
            pooja=True,
            vastu_required=True,
        ),
        style="modern",
    )


@pytest.fixture
def req_1bhk() -> DesignRequirements:
    return DesignRequirements(
        building=BuildingRequirements(
            building_type="apartment",
            floors=1,
            bedrooms=1,
            bathrooms=1,
        ),
    )


@pytest.fixture
def req_5bhk_villa() -> DesignRequirements:
    return DesignRequirements(
        plot=PlotRequirements(width=60.0, length=80.0),
        building=BuildingRequirements(
            building_type="villa",
            floors=2,
            bedrooms=5,
            bathrooms=4,
            parking=True,
            pooja=True,
            office=True,
            balcony=True,
            utility=True,
        ),
    )


# ============================================================================
# RoomProgram Tests
# ============================================================================


class TestRoomProgram:
    def test_create_room(self):
        room = RoomProgram(
            id="living_1",
            room_type="living",
            name="Living Room",
            target_area=180.0,
            privacy_level=PrivacyLevel.PUBLIC,
        )
        assert room.id == "living_1"
        assert room.target_area == 180.0
        assert room.privacy_level == PrivacyLevel.PUBLIC

    def test_room_defaults(self):
        room = RoomProgram(id="bedroom_1", room_type="bedroom")
        assert room.required is True
        assert room.floor_preference == FloorPreference.ANY
        assert room.circulation_importance == 0.5

    def test_room_serialization(self):
        room = RoomProgram(
            id="kitchen_1",
            room_type="kitchen",
            name="Kitchen",
            target_area=140.0,
            adjacency_preferences=frozenset({"dining"}),
        )
        d = room.to_dict()
        restored = RoomProgram.from_dict(d)
        assert restored.id == room.id
        assert restored.target_area == room.target_area

    def test_room_equality(self):
        r1 = RoomProgram(id="bed1", room_type="bedroom")
        r2 = RoomProgram(id="bed1", room_type="bedroom")
        assert r1 == r2

    def test_room_inequality(self):
        r1 = RoomProgram(id="bed1", room_type="bedroom")
        r2 = RoomProgram(id="bed2", room_type="bedroom")
        assert r1 != r2

    def test_room_hash(self):
        r1 = RoomProgram(id="bed1", room_type="bedroom")
        r2 = RoomProgram(id="bed1", room_type="bedroom")
        assert hash(r1) == hash(r2)

    def test_privacy_level_values(self):
        assert PrivacyLevel.PUBLIC.value == "public"
        assert PrivacyLevel.PRIVATE.value == "private"
        assert PrivacyLevel.SEMI_PRIVATE.value == "semi_private"
        assert PrivacyLevel.SERVICE.value == "service"

    def test_floor_preference_values(self):
        assert FloorPreference.GROUND.value == "ground"
        assert FloorPreference.UPPER.value == "upper"
        assert FloorPreference.ANY.value == "any"



class TestSpaceProgram:
    def test_empty_program(self):
        prog = SpaceProgram()
        assert prog.room_count == 0
        assert prog.bedroom_count == 0
        assert prog.bathroom_count == 0
        assert prog.required_rooms == ()

    def test_program_with_rooms(self):
        rooms = (
            RoomProgram(id="living", room_type="living", target_area=180.0),
            RoomProgram(id="bed1", room_type="bedroom", target_area=140.0, required=True),
            RoomProgram(id="parking", room_type="parking", target_area=220.0, required=False),
        )
        prog = SpaceProgram(rooms=rooms, total_target_area=540.0, floor_count=1)
        assert prog.room_count == 3
        assert prog.bedroom_count == 1
        assert len(prog.required_rooms) == 2
        assert len(prog.optional_rooms) == 1

    def test_program_serialization(self):
        rooms = (
            RoomProgram(id="living", room_type="living", target_area=180.0),
            RoomProgram(id="bed1", room_type="bedroom", target_area=140.0),
        )
        prog = SpaceProgram(rooms=rooms, total_target_area=320.0)
        d = prog.to_dict()
        restored = SpaceProgram.from_dict(d)
        assert restored.room_count == 2
        assert restored.total_target_area == 320.0


class TestSpaceProgramGenerator:
    def test_3bhk_duplex(self, generator, req_3bhk):
        prog = generator.generate(req_3bhk)
        assert prog.floor_count == 2
        assert prog.bedroom_count == 3
        assert prog.bathroom_count == 3
        assert prog.room_count >= 10

    def test_1bhk_apartment(self, generator, req_1bhk):
        prog = generator.generate(req_1bhk)
        assert prog.floor_count == 1
        assert prog.bedroom_count == 1
        assert prog.bathroom_count == 2

    def test_5bhk_villa(self, generator, req_5bhk_villa):
        prog = generator.generate(req_5bhk_villa)
        assert prog.floor_count == 2
        assert prog.bedroom_count == 5
        assert prog.bathroom_count >= 4

    def test_living_always_present(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=1))
        prog = generator.generate(req)
        room_types = [r.room_type for r in prog.rooms]
        assert "living" in room_types

    def test_parking_when_requested(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2, parking=True))
        prog = generator.generate(req)
        room_types = [r.room_type for r in prog.rooms]
        assert "parking" in room_types

    def test_pooja_when_requested(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2, pooja=True))
        prog = generator.generate(req)
        room_types = [r.room_type for r in prog.rooms]
        assert "pooja" in room_types

    def test_stair_for_multifloor(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2, floors=2))
        prog = generator.generate(req)
        room_types = [r.room_type for r in prog.rooms]
        assert "stair" in room_types

    def test_master_bedroom_has_bathroom_req(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        master_bath = [r for r in prog.rooms if r.id == "bathroom_master"]
        assert len(master_bath) == 1
        assert "master_bedroom" in master_bath[0].adjacency_requirements

    def test_areas_reasonable(self, generator, req_3bhk):
        prog = generator.generate(req_3bhk)
        for room in prog.rooms:
            if room.target_area is not None and room.minimum_area is not None:
                assert room.minimum_area <= room.target_area

    def test_circulation_area(self, generator, req_1bhk):
        prog = generator.generate(req_1bhk)
        assert prog.circulation_area > 0
        assert prog.usable_area > 0



class TestPrivacyAssignment:
    def test_living_is_public(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        living = [r for r in prog.rooms if r.room_type == "living"][0]
        assert living.privacy_level == PrivacyLevel.PUBLIC

    def test_bedroom_is_private(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        bedrooms = [r for r in prog.rooms if r.room_type == "bedroom"]
        for bed in bedrooms:
            assert bed.privacy_level == PrivacyLevel.PRIVATE

    def test_kitchen_is_semi_private(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        kitchen = [r for r in prog.rooms if r.room_type == "kitchen"][0]
        assert kitchen.privacy_level == PrivacyLevel.SEMI_PRIVATE

    def test_parking_is_service(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2, parking=True))
        prog = generator.generate(req)
        parking = [r for r in prog.rooms if r.room_type == "parking"][0]
        assert parking.privacy_level == PrivacyLevel.SERVICE


class TestVastuAssignment:
    def test_kitchen_south_east(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        kitchen = [r for r in prog.rooms if r.room_type == "kitchen"][0]
        assert kitchen.vastu_preference == "south-east"

    def test_pooja_north_east(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2, pooja=True))
        prog = generator.generate(req)
        pooja = [r for r in prog.rooms if r.room_type == "pooja"][0]
        assert pooja.vastu_preference == "north-east"

    def test_master_bedroom_south_west(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        master = [r for r in prog.rooms if r.room_type == "master_bedroom"][0]
        assert master.vastu_preference == "south-west"


class TestAdjacency:
    def test_kitchen_prefers_dining(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        kitchen = [r for r in prog.rooms if r.room_type == "kitchen"][0]
        assert "dining" in kitchen.adjacency_preferences

    def test_master_bedroom_requires_bathroom(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=2))
        prog = generator.generate(req)
        master = [r for r in prog.rooms if r.room_type == "master_bedroom"][0]
        assert "bathroom" in master.adjacency_requirements


class TestDeterminism:
    def test_same_output_repeated(self, generator, req_3bhk):
        r1 = generator.generate(req_3bhk)
        r2 = generator.generate(req_3bhk)
        assert r1 == r2

    def test_serialization_roundtrip(self, generator, req_3bhk):
        prog = generator.generate(req_3bhk)
        d = prog.to_dict()
        restored = SpaceProgram.from_dict(d)
        assert restored.room_count == prog.room_count
        assert restored.total_target_area == prog.total_target_area


class TestEdgeCases:
    def test_10bhk(self, generator):
        req = DesignRequirements(building=BuildingRequirements(bedrooms=10, floors=3))
        prog = generator.generate(req)
        assert prog.bedroom_count == 10
        assert prog.floor_count == 3

    def test_no_bedrooms_defaults(self, generator):
        req = DesignRequirements()
        prog = generator.generate(req)
        assert prog.bedroom_count == 1
        assert prog.floor_count == 1

    def test_all_features(self, generator):
        req = DesignRequirements(
            building=BuildingRequirements(
                bedrooms=3, parking=True, pooja=True,
                office=True, balcony=True, utility=True,
            )
        )
        prog = generator.generate(req)
        room_types = {r.room_type for r in prog.rooms}
        assert "parking" in room_types
        assert "pooja" in room_types
        assert "office" in room_types
        assert "balcony" in room_types
        assert "utility" in room_types
