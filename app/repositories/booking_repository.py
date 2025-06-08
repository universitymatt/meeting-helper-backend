from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from app.db.models import Booking
from app.schemas.booking import BookingRequestResponse
from app.repositories.base_repository import BaseRepository
from app.schemas.times import Times


class BookingRepository(BaseRepository):
    """Booking repository containing methods for interacting with bookings in the database"""

    def get_all_your_bookings(self, user_id: str) -> List[Booking]:
        return self.db.query(Booking).filter(Booking.user_id == user_id).all()

    def get_your_booking(self, user_id: int, id: int) -> Booking:
        return (
            self.db.query(Booking)
            .filter(Booking.id == id, Booking.user_id == user_id)
            .first()
        )

    def update_booking(self, booking: Booking, desired_times: Times):
        booking.start_time = desired_times.start_datetime
        booking.end_time = desired_times.end_datetime
        self.db.commit()
        return booking

    def get_any_booking(self, id: int) -> Booking:
        return self.db.query(Booking).filter(Booking.id == id).first()

    def accept_booking(self, booking: Booking) -> Booking:
        booking.accepted = True
        booking.datetime_made = datetime.now()

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def create_booking_in_db(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def get_all_requests(self) -> List[Booking]:
        return (
            self.db.query(Booking)
            .options(joinedload(Booking.user))
            .filter(Booking.accepted == False)
            .order_by(Booking.start_time)
            .all()
        )

    def delete_booking(self, booking: Booking) -> List[Booking]:
        try:
            self.db.delete(booking)
            self.db.commit()
            return {
                "id": booking.id,
                "message": f"Successfully deleted booking with id {booking.id}",
            }
        except:
            self.db.rollback()
            raise HTTPException(
                status_code=500, detail="Database error occurred while deleting booking"
            )
