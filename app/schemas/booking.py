from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated
from app.schemas.times import Times


class BookingCreate(Times):
    room_number: Annotated[str, Field(min_length=1)]


class BookingRequestResponse(BaseModel):
    id: int
    user_id: int
    username: str
    start_time: datetime
    end_time: datetime
    accepted: bool
    room_number: str
    datetime_made: datetime

    class Config:
        from_attributes = True
