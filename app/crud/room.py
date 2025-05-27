from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.models import Booking
from app.db.models import Room
from app.schemas.room import RoomCreate

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
  # then check that the room id is not in the subquery
  subquery = (
      db.query(Booking.room_number)
      .filter(
          Booking.start_time <= desired_start,
          Booking.end_time > desired_end
      ).filter(
          Booking.start_time < desired_start,
          Booking.end_time > desired_end
      ).filter(
          Booking.start_time > desired_start,
          Booking.end_time <= desired_end
      )
      .subquery()
  )

  return get_rooms_capacity(db, min_capacity).filter(Room.room_number.not_in(subquery)).all()

def convert_to_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    # checks that its a valid datetime str 
    try:
        dt = datetime.strptime(date_str, fmt)
        if dt.minute % 15 == 0:
            return dt
    except ValueError:
        return None