from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from dateutil.parser import parse
from app.db.models import Booking
from app.db.models import Room

def get_room(db: Session, room_number: int) -> Room:
    return db.query(Room).filter(Room.room_number == room_number).first()

def create_room_in_db(db: Session, room: Room) -> Room:
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def delete_room_in_db(db: Session, room: Room) -> Room:
    db.delete(room)
    db.commit()
    return room

def get_rooms_capacity(db: Session, min_capacity: int):
    return db.query(Room).filter(Room.capacity >= min_capacity)

def get_available_rooms_capacity(db: Session, min_capacity: int) -> List[Room]:
    return get_rooms_capacity(db, min_capacity).all()

def get_available_rooms_time(db: Session, min_capacity: int, desired_start: datetime, desired_end: datetime) -> List[Room]:
    all_rooms = get_rooms_capacity(db, min_capacity).all()
    conflicting_rooms = set(
        room_number for (room_number,) in db.query(Booking.room_number)
        .filter(
            Booking.start_time < desired_end,
            Booking.end_time > desired_start
        )
        .distinct()
        .all()
    )
    
    available_rooms = []
    unavailable_rooms = []
    
    for room in all_rooms:
        room_dict = {**room.__dict__}
        if room.room_number not in conflicting_rooms:
            room_dict["available"] = True
            available_rooms.append(room_dict)
        else:
            room_dict["available"] = False
            unavailable_rooms.append(room_dict)
    
    return available_rooms + unavailable_rooms

def room_is_available(db: Session, room_number: str, desired_start: datetime, desired_end: datetime) -> bool:
    conflicting_bookings = (
        db.query(Booking)
        .filter(
            Booking.room_number == room_number,
            Booking.start_time < desired_end,
            Booking.end_time > desired_start
        )
        .first()
    )
    return conflicting_bookings is None

def convert_to_datetime(date_str: str) -> Optional[datetime]:
    # checks that its a valid datetime str 
    try:
        dt = parse(date_str)
        if dt.minute % 15 == 0:
            return dt
    except ValueError:
        return None
    
def convert_times(start_datestr: str, end_datestr: str):
    valid_start = convert_to_datetime(start_datestr)
    valid_end = convert_to_datetime(end_datestr)
    if not(valid_start and valid_end):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Desired start or end times are invalid")
    if valid_start <= datetime.now(valid_start.tzinfo):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start must be in the future")
    if valid_start >= valid_end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start must be before end")
    return {"start_datetime": valid_start, "end_datetime": valid_end }