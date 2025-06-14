from typing import List
from fastapi import Depends, HTTPException, status
from app.db.models import Booking, User
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.booking import BookingCreate, BookingRequestResponse
from app.schemas.times import Times
from app.services.exception_wrapper import handle_db_exceptions
from datetime import datetime


class BookingService:
    """Service injects repositories (which contains DB connections)"""

    def __init__(
        self,
        booking_repo: BookingRepository = Depends(),
        room_repo: RoomRepository = Depends(),
    ):
        self.booking_repo = booking_repo
        self.room_repo = room_repo

    @handle_db_exceptions
    def booking_logic(
        self, booking: BookingCreate, is_request: bool, current_user: User
    ):
        # check the room exists
        room = self.room_repo.get_room(booking.room_number)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Room does not exist"
            )
        if room.request_only and is_request == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Room is request only"
            )

        # Check user has at least 1 of the allowed roles to book the room if the room has allowed roles
        if room.allowed_role_names and not any(
            role in current_user.role_names for role in room.allowed_role_names
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        # check the room is available
        if not self.room_repo.room_is_available(
            booking.room_number,
            booking.start_datetime,
            booking.end_datetime,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Room is unavailable"
            )

        # make the booking
        new_booking = Booking(
            user_id=current_user.id,
            room_number=booking.room_number,
            start_time=booking.start_datetime,
            end_time=booking.end_datetime,
            accepted=not is_request,
            datetime_made=datetime.now(),
        )

        return self.booking_repo.create_booking_in_db(new_booking)

    @handle_db_exceptions
    def get_all_your_bookings(self, user_id: str) -> List[Booking]:
        return self.booking_repo.get_all_your_bookings(user_id)

    @handle_db_exceptions
    def get_your_booking(self, user_id: int, booking_id: int) -> Booking:
        return self.booking_repo.get_your_booking(user_id, booking_id)

    @handle_db_exceptions
    def update_booking(self, booking: Booking, desired_times: Times) -> Booking:
        if not self.room_repo.room_is_available(
            booking.room_number,
            desired_times.start_datetime,
            desired_times.end_datetime,
            booking.id,
        ):
            raise HTTPException(
                status_code=400,
                detail="Booking cannot be updated as there are conflicting bookings",
            )
        return self.booking_repo.update_booking(booking, desired_times)

    @handle_db_exceptions
    def get_any_booking(self, booking_id: int) -> Booking:
        return self.booking_repo.get_any_booking(booking_id)

    @handle_db_exceptions
    def get_all_requests(self) -> List[BookingRequestResponse]:
        bookings = self.booking_repo.get_all_requests()
        return [
            BookingRequestResponse(
                id=booking.id,
                user_id=booking.user_id,
                username=booking.user.username,
                start_time=booking.start_time,
                end_time=booking.end_time,
                accepted=booking.accepted,
                datetime_made=booking.datetime_made,
                room_number=booking.room_number,
            )
            for booking in bookings
        ]

    @handle_db_exceptions
    def accept_booking(self, booking: Booking):
        room_is_available = self.room_repo.room_is_available(
            booking.room_number, booking.start_time, booking.end_time
        )
        if room_is_available:
            return self.booking_repo.accept_booking(booking)
        else:
            raise HTTPException(
                status_code=400,
                detail="Booking cannot be made as there are conflicting bookings",
            )

    def delete_booking(self, booking: Booking) -> List[Booking]:
        return self.booking_repo.delete_booking(booking)
