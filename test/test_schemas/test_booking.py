import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.schemas.booking import BookingCreate, BookingRequestResponse


class TestBookingCreate:
    """Test the BookingCreate schema"""

    def test_valid_booking_create(self):
        """Test valid booking creation"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        booking = BookingCreate(
            start_datetime=future_time, end_datetime=end_time, room_number="A101"
        )

        assert booking.room_number == "A101"
        assert booking.start_datetime == future_time
        assert booking.end_datetime == end_time

    def test_missing_room_number(self):
        """Test that missing room_number raises ValidationError"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        with pytest.raises(ValidationError):
            BookingCreate(start_datetime=future_time, end_datetime=end_time)

    def test_empty_room_number(self):
        """Test that empty room_number raises ValidationError"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        with pytest.raises(ValidationError):
            BookingCreate(
                start_datetime=future_time, end_datetime=end_time, room_number=""
            )

    def test_inherits_times_validation(self):
        """Test that BookingCreate inherits Times validation"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        past_time = past_time.replace(minute=0, second=0, microsecond=0)
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)

        with pytest.raises(ValidationError) as exc_info:
            BookingCreate(
                start_datetime=past_time, end_datetime=future_time, room_number="A101"
            )

        assert "Start time must be in the future" in str(exc_info.value)


class TestBookingRequestResponse:
    """Test the BookingRequestResponse schema"""

    def test_valid_booking_response(self):
        """Test valid booking response creation"""
        now = datetime.now(timezone.utc)
        future_time = now + timedelta(hours=1)

        booking_data = {
            "id": 1,
            "user_id": 123,
            "username": "testuser",
            "start_time": future_time,
            "end_time": future_time + timedelta(hours=1),
            "accepted": True,
            "room_number": "A101",
            "datetime_made": now,
        }

        booking = BookingRequestResponse(**booking_data)

        assert booking.id == 1
        assert booking.user_id == 123
        assert booking.username == "testuser"
        assert booking.accepted is True
        assert booking.room_number == "A101"

    def test_required_fields(self):
        """Test that all required fields must be provided"""
        with pytest.raises(ValidationError):
            BookingRequestResponse()

    @pytest.mark.parametrize(
        "field",
        [
            "id",
            "user_id",
            "username",
            "start_time",
            "end_time",
            "accepted",
            "room_number",
            "datetime_made",
        ],
    )
    def test_missing_required_field(self, field):
        """Test that missing any required field raises ValidationError"""
        now = datetime.now(timezone.utc)
        future_time = now + timedelta(hours=1)

        booking_data = {
            "id": 1,
            "user_id": 123,
            "username": "testuser",
            "start_time": future_time,
            "end_time": future_time + timedelta(hours=1),
            "accepted": True,
            "room_number": "A101",
            "datetime_made": now,
        }

        del booking_data[field]

        with pytest.raises(ValidationError):
            BookingRequestResponse(**booking_data)
