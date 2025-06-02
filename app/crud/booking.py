from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Booking

def get_booking(user_id: int, id: int, db: Session) -> Booking:
    return db.query(Booking).filter(Booking.id == id, Booking.user_id == user_id).first()

def create_booking_in_db(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def get_your_bookings(user_id: str, db: Session) -> List[Booking]:
    return db.query(Booking).filter(Booking.user_id == user_id).all()


def delete_booking(user_id: int, id: int, db: Session) -> List[Booking]:
    try:
        booking = get_booking(user_id, id, db)
        if not booking:
            raise HTTPException(
                    status_code=404, 
                    detail="Booking not found or you don't have permission to delete it"
                )
        db.delete(booking)
        db.commit()
        return {"id": id, "message": f"Successfully deleted booking with id {id}"}
    except:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while deleting booking"
        )