"""Deterministic sample architectural projects.

These sample programs are intended for integration testing, documentation,
regression testing, performance benchmarking, Flutter demos, and API examples.
No randomness. No AI. Only deterministic reference programs.
"""

from __future__ import annotations

from ..ai.room_program import FloorPreference, PrivacyLevel, RoomProgram
from ..ai.space_program import SpaceProgram
from ..types import RoomType


class SampleProjects:
    """Reusable deterministic architectural sample projects."""

    @staticmethod
    def one_bhk() -> SpaceProgram:
        rooms = (
            RoomProgram(
                id="living",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=18.0,
                minimum_area=12.0,
                maximum_area=24.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="kitchen",
                room_type=RoomType.KITCHEN,
                name="Kitchen",
                target_area=12.0,
                minimum_area=8.0,
                maximum_area=16.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="bedroom",
                room_type=RoomType.BEDROOM,
                name="Bedroom",
                target_area=14.0,
                minimum_area=10.0,
                maximum_area=18.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="bathroom",
                room_type=RoomType.BATHROOM,
                name="Bathroom",
                target_area=6.0,
                minimum_area=4.0,
                maximum_area=8.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
        )
        return SampleProjects._build_program("one_bhk", rooms, floor_count=1)

    @staticmethod
    def two_bhk() -> SpaceProgram:
        rooms = (
            RoomProgram(
                id="living",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=20.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="kitchen",
                room_type=RoomType.KITCHEN,
                name="Kitchen",
                target_area=12.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="master_bedroom",
                room_type=RoomType.BEDROOM,
                name="Master Bedroom",
                target_area=16.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bedroom",
                room_type=RoomType.BEDROOM,
                name="Bedroom",
                target_area=12.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bathroom",
                room_type=RoomType.BATHROOM,
                name="Bathroom",
                target_area=8.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.ANY,
            ),
            RoomProgram(
                id="dining",
                room_type=RoomType.DINING,
                name="Dining Room",
                target_area=12.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
        )
        return SampleProjects._build_program("two_bhk", rooms, floor_count=1)

    @staticmethod
    def three_bhk() -> SpaceProgram:
        rooms = (
            RoomProgram(
                id="living",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=22.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="kitchen",
                room_type=RoomType.KITCHEN,
                name="Kitchen",
                target_area=14.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="dining",
                room_type=RoomType.DINING,
                name="Dining Room",
                target_area=12.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="master_bedroom",
                room_type=RoomType.BEDROOM,
                name="Master Bedroom",
                target_area=16.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bedroom2",
                room_type=RoomType.BEDROOM,
                name="Bedroom 2",
                target_area=12.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bedroom3",
                room_type=RoomType.BEDROOM,
                name="Bedroom 3",
                target_area=12.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bathroom",
                room_type=RoomType.BATHROOM,
                name="Bathroom",
                target_area=8.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.ANY,
            ),
            RoomProgram(
                id="utility",
                room_type=RoomType.UTILITY,
                name="Utility Room",
                target_area=6.0,
                privacy_level=PrivacyLevel.SERVICE,
                floor_preference=FloorPreference.GROUND,
            ),
        )
        return SampleProjects._build_program("three_bhk", rooms, floor_count=1)

    @staticmethod
    def duplex() -> SpaceProgram:
        rooms = (
            RoomProgram(
                id="living",
                room_type=RoomType.LIVING,
                name="Living Room",
                target_area=20.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="kitchen",
                room_type=RoomType.KITCHEN,
                name="Kitchen",
                target_area=12.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="dining",
                room_type=RoomType.DINING,
                name="Dining Room",
                target_area=12.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="guest_bedroom",
                room_type=RoomType.BEDROOM,
                name="Guest Bedroom",
                target_area=12.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="bathroom_ground",
                room_type=RoomType.BATHROOM,
                name="Bathroom",
                target_area=8.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="master_bedroom",
                room_type=RoomType.BEDROOM,
                name="Master Bedroom",
                target_area=16.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bedroom",
                room_type=RoomType.BEDROOM,
                name="Bedroom",
                target_area=12.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="family_lounge",
                room_type=RoomType.LIVING,
                name="Family Lounge",
                target_area=14.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
            RoomProgram(
                id="bathroom_upper",
                room_type=RoomType.BATHROOM,
                name="Bathroom",
                target_area=8.0,
                privacy_level=PrivacyLevel.PRIVATE,
                floor_preference=FloorPreference.UPPER,
            ),
        )
        return SampleProjects._build_program("duplex", rooms, floor_count=2)

    @staticmethod
    def small_office() -> SpaceProgram:
        rooms = (
            RoomProgram(
                id="reception",
                room_type=RoomType.LIVING,
                name="Reception",
                target_area=14.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="office",
                room_type=RoomType.STORAGE,
                name="Office",
                target_area=14.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="meeting",
                room_type=RoomType.DINING,
                name="Meeting Room",
                target_area=12.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="pantry",
                room_type=RoomType.UTILITY,
                name="Pantry",
                target_area=8.0,
                privacy_level=PrivacyLevel.SERVICE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="toilet",
                room_type=RoomType.TOILET,
                name="Toilet",
                target_area=6.0,
                privacy_level=PrivacyLevel.SERVICE,
                floor_preference=FloorPreference.GROUND,
            ),
        )
        return SampleProjects._build_program("small_office", rooms, floor_count=1)

    @staticmethod
    def retail_shop() -> SpaceProgram:
        rooms = (
            RoomProgram(
                id="shop",
                room_type=RoomType.LIVING,
                name="Shop",
                target_area=18.0,
                privacy_level=PrivacyLevel.PUBLIC,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="storage",
                room_type=RoomType.STORAGE,
                name="Storage",
                target_area=10.0,
                privacy_level=PrivacyLevel.SERVICE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="office",
                room_type=RoomType.STORAGE,
                name="Office",
                target_area=10.0,
                privacy_level=PrivacyLevel.SEMI_PRIVATE,
                floor_preference=FloorPreference.GROUND,
            ),
            RoomProgram(
                id="toilet",
                room_type=RoomType.TOILET,
                name="Toilet",
                target_area=6.0,
                privacy_level=PrivacyLevel.SERVICE,
                floor_preference=FloorPreference.GROUND,
            ),
        )
        return SampleProjects._build_program("retail_shop", rooms, floor_count=1)

    @staticmethod
    def _build_program(name: str, rooms: tuple[RoomProgram, ...], floor_count: int) -> SpaceProgram:
        total_target = sum(room.target_area or 0.0 for room in rooms)
        circulation_area = total_target * 0.15
        usable_area = total_target
        return SpaceProgram(
            rooms=rooms,
            total_target_area=total_target,
            circulation_area=circulation_area,
            usable_area=usable_area,
            floor_count=floor_count,
            metadata={"sample": name},
        )
