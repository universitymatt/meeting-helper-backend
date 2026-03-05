from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated
from app.schemas.times import Times


class BookingCreate(Times):
    room_number: Annotated[str, Field(min_length=1)]


class BookingRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    username: str
    start_time: datetime
    end_time: datetime
    accepted: bool
    room_number: str
    datetime_made: datetime
