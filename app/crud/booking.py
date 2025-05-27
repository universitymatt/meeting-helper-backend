from sqlalchemy.orm import Session
from app.db.models import Booking

def get_room(db: Session, id: int) -> Booking:
    return db.query(Booking).filter(Booking.id == id).first()

def create_booking_in_db(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking