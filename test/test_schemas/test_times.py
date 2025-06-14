import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.schemas.times import Times


class TestTimes:
    """Test the Times schema validation"""

    def test_valid_times(self):
        """Test valid time inputs"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        # Ensure minute is in 15-minute intervals
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        times = Times(start_datetime=future_time, end_datetime=end_time)

        assert times.start_datetime == future_time
        assert times.end_datetime == end_time

    @pytest.mark.parametrize("minute", [0, 15, 30, 45])
    def test_valid_15_minute_intervals(self, minute):
        """Test that 15-minute intervals are accepted"""
        base_time = datetime.now(timezone.utc) + timedelta(hours=1)
        start_time = base_time.replace(minute=minute, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        times = Times(start_datetime=start_time, end_datetime=end_time)
        assert times.start_datetime.minute == minute

    @pytest.mark.parametrize("minute", [1, 5, 10, 14, 16, 20, 25, 35, 40, 50, 59])
    def test_invalid_15_minute_intervals(self, minute):
        """Test that non-15-minute intervals raise ValidationError"""
        base_time = datetime.now(timezone.utc) + timedelta(hours=1)
        start_time = base_time.replace(minute=minute, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)

        with pytest.raises(ValidationError) as exc_info:
            Times(start_datetime=start_time, end_datetime=end_time)

        assert "Time must be in 15-minute intervals" in str(exc_info.value)

    def test_start_time_in_past(self):
        """Test that start time in the past raises ValidationError"""
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        past_time = past_time.replace(minute=0, second=0, microsecond=0)
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)

        with pytest.raises(ValidationError) as exc_info:
            Times(start_datetime=past_time, end_datetime=future_time)

        assert "Start time must be in the future" in str(exc_info.value)

    def test_start_time_equals_end_time(self):
        """Test that equal start and end times raise ValidationError"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)

        with pytest.raises(ValidationError) as exc_info:
            Times(start_datetime=future_time, end_datetime=future_time)

        assert "Start time must be before end time" in str(exc_info.value)

    def test_start_time_after_end_time(self):
        """Test that start time after end time raises ValidationError"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        earlier_time = future_time - timedelta(hours=1)

        with pytest.raises(ValidationError) as exc_info:
            Times(start_datetime=future_time, end_datetime=earlier_time)

        assert "Start time must be before end time" in str(exc_info.value)

    def test_timezone_aware_datetimes(self):
        """Test that timezone-aware datetimes work correctly"""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        future_time = future_time.replace(minute=0, second=0, microsecond=0)
        end_time = future_time + timedelta(hours=1)

        times = Times(start_datetime=future_time, end_datetime=end_time)
        assert times.start_datetime.tzinfo is not None
        assert times.end_datetime.tzinfo is not None
