from pydantic import BaseModel

class Times(BaseModel):
    start_datestr: str
    end_datestr: str 

class BookingCreate(BaseModel):
    room_number: str
    times: Times