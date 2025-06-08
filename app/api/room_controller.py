from app.api.dependencies import get_current_user, require_role
from app.db.models import User
from app.schemas.room import GetRooms, RoomCreate
from fastapi import APIRouter, Depends, Query
from app.services.room_service import RoomService
import logging

logger = logging.getLogger("app.rooms")

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])


@room_router.get("")
def get_available_rooms(
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(),
    filters: GetRooms = Query(),
):
    logger.info(
        f"User {current_user.id} searching for available rooms with capacity {filters.min_capacity}"
    )

    try:
        # get available rooms
        rooms = room_service.get_available_rooms_time(
            filters.min_capacity, filters.start_datetime, filters.end_datetime
        )

        # Add permission checking to each room
        for room_dict in rooms:
            room_dict["sufficient_roles"] = RoomService.check_user_has_room_permissions(
                room_dict, current_user
            )

        logger.info(f"Found {len(rooms)} available rooms for user {current_user.id}")
        return {"filters": filters, "rooms": rooms}

    except Exception as e:
        logger.error(
            f"Failed to get available rooms for user {current_user.id}: {str(e)}"
        )
        raise


@room_router.get("/all")
def get_all_rooms(
    current_user: User = Depends(get_current_user),
    room_service: RoomService = Depends(),
):
    logger.info(f"User {current_user.id} fetching all rooms")

    try:
        result = room_service.get_all_rooms()
        logger.debug(f"Retrieved all rooms for user {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to get all rooms for user {current_user.id}: {str(e)}")
        raise


@room_router.post("")
def create_room(
    room: RoomCreate,
    _: User = Depends(require_role(["admin"])),
    room_service: RoomService = Depends(),
):
    logger.info(f"Admin creating new room: {room.room_number}")

    result = room_service.create_room(room)
    logger.info(f"Room {room.room_number} created successfully")
    return result


@room_router.delete("/{room_number}")
def delete_room(
    room_number: str,
    _: User = Depends(require_role(["admin"])),
    room_service: RoomService = Depends(),
):
    logger.info(f"Admin deleting room: {room_number}")

    try:
        result = room_service.delete_room(room_number)
        logger.info(f"Room {room_number} deleted successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to delete room {room_number}: {str(e)}")
        raise
