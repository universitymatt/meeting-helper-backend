from pydantic import BaseModel, Field
from typing import Optional

class Times(BaseModel):
  start_datestr: str
  end_datestr: str 

class GetRooms(BaseModel):
  min_capacity: int = 0
  times: Times = None

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
