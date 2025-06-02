from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.get_db import get_db
from app.crud.booking import create_booking_in_db, delete_booking, get_your_bookings
from app.crud.room import convert_times, get_room, room_is_available
from app.auth.utils import get_current_user
from app.schemas.booking import BookingCreate
from app.db.models import Booking, User

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])

@booking_router.post("")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  # check the user exists and store thier id
  user_id = current_user.id
  # check times are valid
  valid_times = convert_times(booking.times.start_datestr, booking.times.end_datestr)
  if not valid_times:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Desired start or end times are invalid")
  # check the room exists
  if not get_room(db, booking.room_number):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room does not exist")
  # check the room is available
  if not room_is_available(db, booking.room_number, valid_times["start_datetime"], valid_times["end_datetime"]):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room is unavailable")
  if valid_times["start_datetime"] == valid_times["end_datetime"]:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking start and end times cannot be the same")
  # make the booking
  new_booking = Booking(
    user_id=user_id,
    room_number=booking.room_number,
    start_time=valid_times["start_datetime"],
    end_time=valid_times["end_datetime"],
  )
  return create_booking_in_db(db, new_booking)

@booking_router.get("")
def get_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  user_id = current_user.id
  return get_your_bookings(user_id, db)

@booking_router.delete("/{booking_id}")
def delete_your_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  user_id = current_user.id
  return delete_booking(user_id, booking_id, db)
