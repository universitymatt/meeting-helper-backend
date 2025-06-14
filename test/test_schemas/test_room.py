import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.schemas.room import GetRooms, RoomCreate


class TestGetRooms:
    """Test the GetRooms schema"""

    def test_valid_get_rooms(self):
        """Test valid GetRooms creation"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        get_rooms = GetRooms(
            start_datetime=future_time, end_datetime=end_time, min_capacity=5
        )

        assert get_rooms.min_capacity == 5
        assert get_rooms.start_datetime == future_time
        assert get_rooms.end_datetime == end_time

    def test_default_min_capacity(self):
        """Test that min_capacity defaults to 0"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        get_rooms = GetRooms(start_datetime=future_time, end_datetime=end_time)

        assert get_rooms.min_capacity == 0

    def test_negative_min_capacity(self):
        """Test that negative min_capacity is allowed (validation in business logic)"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        get_rooms = GetRooms(
            start_datetime=future_time, end_datetime=end_time, min_capacity=-1
        )

        assert get_rooms.min_capacity == -1


class TestRoomCreate:
    """Test the RoomCreate schema"""

    def test_valid_room_create_minimal(self):
        """Test valid room creation with minimal data"""
        room = RoomCreate(room_number="A101", capacity=10, description="Test room")

        assert room.room_number == "A101"
        assert room.capacity == 10
        assert room.description == "Test room"
        assert room.request_only is None
        assert room.roles is None

    def test_valid_room_create_full(self):
        """Test valid room creation with all fields"""
        room = RoomCreate(
            room_number="A101",
            capacity=10,
            description="Test room",
            request_only=True,
            roles=["admin", "teacher"],
        )

        assert room.room_number == "A101"
        assert room.capacity == 10
        assert room.description == "Test room"
        assert room.request_only is True
        assert room.roles == ["admin", "teacher"]

    def test_none_values(self):
        """Test that None values are handled correctly"""
        room = RoomCreate(
            room_number="A101",
            capacity=10,
            description=None,
            request_only=None,
            roles=None,
        )

        assert room.description is None
        assert room.request_only is None
        assert room.roles is None

    def test_empty_description(self):
        """Test that empty string description is allowed"""
        room = RoomCreate(room_number="A101", capacity=10, description="")

        assert room.description == ""

    def test_empty_roles_list(self):
        """Test that empty roles list is allowed"""
        room = RoomCreate(
            room_number="A101", capacity=10, description="Test room", roles=[]
        )

        assert room.roles == []

    def test_required_fields(self):
        """Test that required fields must be provided"""
        with pytest.raises(ValidationError):
            RoomCreate(capacity=10, description="Test")

        with pytest.raises(ValidationError):
            RoomCreate(room_number="A101", description="Test")
