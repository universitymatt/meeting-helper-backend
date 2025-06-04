from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.get_db import get_db
from app.crud.booking import accept_booking, create_booking_in_db, delete_booking, get_all_requests, get_any_booking, get_booking, get_your_bookings
from app.crud.room import convert_times, get_room, room_is_available
from app.auth.utils import get_current_user, require_role
from app.schemas.booking import BookingCreate
from app.db.models import Booking, User

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])

def booking_logic(booking: BookingCreate, is_request: bool, db: Session, current_user: User):
  # check the user exists and store thier id
  user_id = current_user.id
  # check times are valid
  valid_times = convert_times(booking.times.start_datestr, booking.times.end_datestr)
  if not valid_times:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Desired start or end times are invalid")
  # check the room exists
  if not get_room(db, booking.room_number, is_request):
    if is_request:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room does not exist")
    else:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room does not exist or is request only")
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
    accepted= not is_request
  )

  return create_booking_in_db(db, new_booking)

@booking_router.post("")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return booking_logic(booking, is_request=False, db=db, current_user=current_user)

@booking_router.post("/request")
def create_booking_request(booking: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return booking_logic(booking, is_request=True, db=db, current_user=current_user)

@booking_router.get("")
def get_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  user_id = current_user.id
  return get_your_bookings(user_id, db)

@booking_router.delete("/{booking_id}")
def delete_a_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
  booking = get_booking(current_user.id, booking_id, db)
  if not booking:
    raise HTTPException(
            status_code=404, 
            detail="Booking not found or you don't have permission to delete it"
        )
  return delete_booking(booking, db)

@booking_router.get("/request")
def get_all_booking_requests( _: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
  return get_all_requests(db)

@booking_router.put("/{booking_id}/approve")
def approve_booking_request(booking_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
  booking = get_any_booking(booking_id, db)
  if not booking:
    raise HTTPException(
            status_code=404, 
            detail="Booking not found"
        )
  booking = accept_booking(booking, db)
  return {"id": booking.id, "message": f"Approved booking request for {booking.id} on room: {booking.room_number}"}

@booking_router.delete("/{booking_id}/decline")
def decline_booking_request(booking_id: int, db: Session = Depends(get_db),  _: User = Depends(require_role(["admin"]))):
  booking = get_any_booking(booking_id, db)
  if not booking:
    raise HTTPException(
            status_code=404, 
            detail="Booking not found"
        )
  return delete_booking(booking, db)