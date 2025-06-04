from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Booking

def get_booking(user_id: int, id: int, db: Session) -> Booking:
    return db.query(Booking).filter(Booking.id == id, Booking.user_id == user_id).first()

def get_any_booking(id: int, db: Session) -> Booking:
    return db.query(Booking).filter(Booking.id == id).first()

def accept_booking(booking: Booking, db: Session) -> Booking:
    booking.accepted = True
    db.commit()
    db.refresh(booking)
    return booking

def create_booking_in_db(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_your_bookings(user_id: str, db: Session) -> List[Booking]:
    return db.query(Booking).filter(Booking.user_id == user_id).all()

def get_all_requests(db: Session) -> List[Booking]:
    return db.query(Booking).filter(Booking.accepted == False).order_by(Booking.start_time).all()

def delete_booking(booking: Booking, db: Session) -> List[Booking]:
    try:
        db.delete(booking)
        db.commit()
        return {"id": booking.id, "message": f"Successfully deleted booking with id {booking.id}"}
    except:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while deleting booking"
        )