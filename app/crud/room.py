from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.models import Booking
from app.db.models import Room

def get_room(db: Session, room_number: int) -> Room:
    return db.query(Room).filter(Room.room_number == room_number).first()

def create_room_in_db(db: Session, room: Room) -> Room:
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def get_rooms_capacity(db: Session, min_capacity: int):
    return db.query(Room).filter(Room.capacity >= min_capacity)

def get_available_rooms_capacity(db: Session, min_capacity: int) -> List[Room]:
    return get_rooms_capacity(db, min_capacity).all()

def get_available_rooms_time(db: Session, min_capacity: int, desired_start: datetime, desired_end: datetime) -> List[Room]:
  # subquery to get conflicting bookings
  subquery = (
      db.query(Booking.room_number)
      .filter(
            Booking.start_time < desired_end,
            Booking.end_time > desired_start
      )
      .subquery()
  )

  # then return the rooms that do not appear in the subquery
  return get_rooms_capacity(db, min_capacity).filter(Room.room_number.not_in(subquery)).all()

def room_is_available(db: Session, room_number: str, desired_start: datetime, desired_end: datetime) -> bool:
    conflicting_bookings = (
        db.query(Booking)
        .filter(
            Booking.room_number == room_number,
            Booking.start_time < desired_end,
            Booking.end_time > desired_start
        )
        .all()
    )
    return not conflicting_bookings 


def convert_to_datetime(date_str: str, fmt: str = "%Y-%m-%dT%H:%M:%S") -> Optional[datetime]:
    # checks that its a valid datetime str 
    try:
        dt = datetime.strptime(date_str, fmt)
        if dt.minute % 15 == 0:
            return dt
    except ValueError:
        return None
    
def convert_times(start_datestr: str, end_datestr: str):
    valid_start = convert_to_datetime(start_datestr)
    valid_end = convert_to_datetime(end_datestr)
    if valid_start and valid_end:
        return {"start_datetime": valid_start, "end_datetime": valid_end }