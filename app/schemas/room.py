from pydantic import BaseModel, Field, model_validator
from typing import Optional
from app.schemas.booking import Times

class GetRooms(BaseModel):
    min_capacity: int = 0
    start_datestr: Optional[str] = None
    end_datestr: Optional[str] = None

    @model_validator(mode="after")
    def check_times_together(self) -> 'GetRooms':
        if (self.start_datestr is None) != (self.end_datestr is None):
            raise ValueError("Both start_datestr and end_datestr must be provided together")
        return self

class RoomCreate(BaseModel):
  room_number: str
  capacity: int
  description: str | None = Field(default = None)
  request_only: bool | None = Field(default = None)


class RoomOut(BaseModel):
  room_number: str
  capacity: int
  description: Optional[str]
  request_only: bool
