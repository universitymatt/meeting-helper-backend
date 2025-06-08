from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


class Times(BaseModel):
    """Required times - both must be provided"""

    start_datetime: datetime
    end_datetime: datetime

    @field_validator("start_datetime", "end_datetime")
    @classmethod
    def validate_15_minute_intervals(cls, v: datetime) -> datetime:
        """Validate 15-minute intervals"""
        if v.minute % 15 != 0:
            raise ValueError("Time must be in 15-minute intervals")
        return v

    @model_validator(mode="after")
    def validate_time_range(self):
        """Validate business rules for required times"""
        if self.start_datetime <= datetime.now(self.start_datetime.tzinfo):
            raise ValueError("Start time must be in the future")

        if self.start_datetime >= self.end_datetime:
            raise ValueError("Start time must be before end time")

        return self
