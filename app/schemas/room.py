from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.times import Times


class GetRooms(Times):
    min_capacity: int = 0


class RoomCreate(BaseModel):
    room_number: str
    capacity: int
    description: str | None = Field(default=None)
    request_only: bool | None = Field(default=None)
    roles: List[str] | None = Field(default=None)
