from app.crud.room import convert_times, convert_to_datetime, create_room_in_db, get_available_rooms_capacity, get_available_rooms_time, get_room
from app.api.get_db import get_db
from app.db.models import Room
from app.schemas.room import GetRooms, RoomCreate
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

@room_router.get("")
def get_available_rooms(room: GetRooms = Depends(), db: Session = Depends(get_db)):
    # get available rooms
    if room.start_datestr and room.end_datestr:
        # check times are valid
        valid_times = convert_times(room.start_datestr, room.end_datestr)
        if valid_times:
            return get_available_rooms_time(db, room.min_capacity, valid_times.start_datetime, valid_times.end_datetime)
        raise HTTPException(status_code=400, detail="Desired start or end times are invalid")
    else:
        # get rooms based on time and capacity = 0
        return get_available_rooms_capacity(db, room.min_capacity)
    
    
@room_router.post("")
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    # check the room doesn't exist
    if get_room(db, room.room_number):
       raise HTTPException(status_code=400, detail=f"Room with room number {room.room_number} already exists")
    # get available rooms
    new_room = Room(**room.model_dump())
    new_room = create_room_in_db(db, new_room)
    return new_room