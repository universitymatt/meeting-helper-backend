from typing import Dict, Any, List
from datetime import datetime
from app.db.models import Booking, Room
from app.repositories.base_repository import BaseRepository


class RoomRepository(BaseRepository):
    """Room repository containing methods for interacting with rooms in the database"""

    def get_all_rooms(self) -> List[Room]:
        return self.db.query(Room).all()

    def get_room(self, room_number: str) -> Room:
        return self.db.query(Room).filter(Room.room_number == room_number).first()

    def create_room_in_db(self, room: Room) -> Room:
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return room

    def delete_room_in_db(self, room: Room) -> Room:
        self.db.delete(room)
        self.db.commit()
        return room

    def get_rooms_capacity(self, min_capacity: int):
        return self.db.query(Room).filter(Room.capacity >= min_capacity)

    def get_rooms_with_availability_check(
        self, min_capacity: int, desired_start: datetime, desired_end: datetime
    ):
        """Get all rooms with sufficient capacity (returns query, not executed)"""
        return self.get_rooms_capacity(min_capacity)

    def get_conflicting_room_numbers(
        self, desired_start: datetime, desired_end: datetime
    ):
        """Get room numbers that have conflicting bookings"""
        return set(
            room_number
            for (room_number,) in self.db.query(Booking.room_number)
            .filter(
                Booking.start_time < desired_end,
                Booking.end_time > desired_start,
                Booking.accepted == True,  # Only consider accepted bookings
            )
            .distinct()
            .all()
        )

    def room_is_available(
        self, room_number: str, desired_start: datetime, desired_end: datetime
    ) -> bool:
        conflicting_bookings = (
            self.db.query(Booking)
            .filter(
                Booking.room_number == room_number,
                Booking.accepted == True,
                Booking.start_time < desired_end,
                Booking.end_time > desired_start,
            )
            .first()
        )
        return conflicting_bookings is None
