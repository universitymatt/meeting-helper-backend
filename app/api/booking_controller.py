from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user, require_role
from app.schemas.booking import BookingCreate
from app.db.models import User
from app.schemas.times import Times
from app.services.booking_service import BookingService
import logging

# Module-specific logger
logger = logging.getLogger("app.bookings")

booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])


@booking_router.post("")
def create_booking(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(),
):
    logger.info(
        f"Creating booking for user {current_user.id}, room {booking.room_number}"
    )

    try:
        result = booking_service.booking_logic(
            booking, is_request=False, current_user=current_user
        )
        logger.info(f"Booking created successfully for user {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to create booking for user {current_user.id}: {str(e)}")
        raise


@booking_router.post("/request")
def create_booking_request(
    booking: BookingCreate,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(),
):
    logger.info(
        f"Creating booking request for user {current_user.id}, room {booking.room_number}"
    )

    try:
        result = booking_service.booking_logic(
            booking, is_request=True, current_user=current_user
        )
        logger.info(f"Booking request created successfully for user {current_user.id}")
        return result
    except Exception as e:
        logger.error(
            f"Failed to create booking request for user {current_user.id}: {str(e)}"
        )
        raise


@booking_router.get("")
def get_bookings(
    booking_service: BookingService = Depends(),
    current_user: User = Depends(get_current_user),
):
    logger.info(f"Fetching bookings for user {current_user.id}")
    user_id = current_user.id
    result = booking_service.get_all_your_bookings(user_id)
    logger.debug(f"Retrieved bookings for user {current_user.id}")
    return result


@booking_router.delete("/{booking_id}")
def delete_a_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(),
):
    logger.info(f"User {current_user.id} attempting to delete booking {booking_id}")

    booking = booking_service.get_your_booking(current_user.id, booking_id)
    if not booking:
        logger.warning(
            f"Booking {booking_id} not found or unauthorized for user {current_user.id}"
        )
        raise HTTPException(
            status_code=404,
            detail="Booking not found or you don't have permission to delete it",
        )

    result = booking_service.delete_booking(booking)
    logger.info(f"Booking {booking_id} deleted successfully by user {current_user.id}")
    return result


@booking_router.get("/request")
def get_all_booking_requests(
    _: User = Depends(require_role(["admin"])),
    booking_service: BookingService = Depends(),
):
    logger.info("Admin fetching all booking requests")
    result = booking_service.get_all_requests()
    logger.debug(f"Retrieved booking requests")
    return result


@booking_router.put("/{booking_id}/approve")
def approve_booking_request(
    booking_id: int,
    booking_service: BookingService = Depends(),
    _: User = Depends(require_role(["admin"])),
):
    logger.info(f"Admin approving booking request {booking_id}")

    booking = booking_service.get_any_booking(booking_id)
    if not booking:
        logger.warning(f"Booking {booking_id} not found for approval")
        raise HTTPException(status_code=404, detail="Booking not found")

    # need to add in check whether booking is still valid
    booking = booking_service.accept_booking(booking)
    logger.info(f"Booking request {booking_id} approved successfully")

    return {
        "id": booking.id,
        "message": f"Approved booking request for {booking.id} on room: {booking.room_number}",
    }


@booking_router.put("/{booking_id}")
def update_booking(
    booking_id: int,
    desired_times: Times,
    booking_service: BookingService = Depends(),
    current_user: User = Depends(get_current_user),
):
    booking = booking_service.get_your_booking(current_user.id, booking_id)
    if not booking:
        msg = f"Booking {booking_id} not found for update"
        logger.warning(msg)
        raise HTTPException(status_code=404, detail=msg)

    return booking_service.update_booking(booking, desired_times)


@booking_router.delete("/{booking_id}/decline")
def decline_booking_request(
    booking_id: int,
    booking_service: BookingService = Depends(),
    _: User = Depends(require_role(["admin"])),
):
    logger.info(f"Admin declining booking request {booking_id}")

    booking = booking_service.get_any_booking(booking_id)
    if not booking:
        logger.warning(f"Booking {booking_id} not found for decline")
        raise HTTPException(status_code=404, detail="Booking not found")

    result = booking_service.delete_booking(booking)
    logger.info(f"Booking request {booking_id} declined successfully")
    return result
