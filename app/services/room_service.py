from typing import Any, Dict, List
from datetime import datetime
from fastapi import Depends, HTTPException, status
from app.db.models import Room, User
from app.repositories.role_repository import RoleRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.room import RoomCreate
from app.services.exception_wrapper import handle_db_exceptions


class RoomService:
    """Service injects repositories (which contains DB connections)"""

    def __init__(
        self,
        room_repo: RoomRepository = Depends(),
        role_repo: RoleRepository = Depends(),
    ):
        self.room_repo = room_repo
        self.role_repo = role_repo

    @staticmethod
    def room_to_dict(room: Room, available: bool = True) -> Dict[str, Any]:
        """Convert Room object to dictionary including relationships"""
        return {
            "room_number": room.room_number,
            "capacity": room.capacity,
            "description": room.description,
            "request_only": room.request_only,
            "allowed_roles": room.allowed_role_names,
            "available": available,
        }

    @staticmethod
    def check_user_has_room_permissions(room_dict: Dict[str, Any], user: User) -> bool:
        """Check if user has sufficient roles to book this room"""
        allowed_roles = room_dict.get("allowed_roles", [])

        # If no role restrictions, anyone can book
        if not allowed_roles:
            return True

        # Check if user has any of the required roles
        return any(role in user.role_names for role in allowed_roles)

    @handle_db_exceptions
    def get_available_rooms_time(
        self, min_capacity: int, desired_start: datetime, desired_end: datetime
    ) -> List[Dict[str, Any]]:
        # Get all rooms with sufficient capacity (with relationships loaded)
        all_rooms = self.room_repo.get_rooms_with_availability_check(
            min_capacity, desired_start, desired_end
        ).all()

        # Get room numbers that have conflicting bookings
        conflicting_rooms = self.room_repo.get_conflicting_room_numbers(
            desired_start, desired_end
        )

        available_rooms = []
        unavailable_rooms = []

        for room in all_rooms:
            if room.room_number not in conflicting_rooms:
                available_rooms.append(RoomService.room_to_dict(room, available=True))
            else:
                unavailable_rooms.append(
                    RoomService.room_to_dict(room, available=False)
                )
        return available_rooms + unavailable_rooms

    @handle_db_exceptions
    def create_room(self, room: RoomCreate):
        # check the room doesn't exist
        if self.room_repo.get_room(room.room_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room with room number already exists",
            )
        # get the roles
        role_list = []
        if room.roles:
            for role_name in room.roles:
                role = self.role_repo.get_role(role_name)
                if not role:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Role '{role_name}' not found",
                    )
                role_list.append(role)
        new_room = Room(
            room_number=room.room_number,
            capacity=room.capacity,
            description=room.description,
            request_only=room.request_only,
            allowed_roles=role_list,
        )
        new_room = self.room_repo.create_room_in_db(new_room)
        return new_room

    @handle_db_exceptions
    def delete_room(self, room_number: str):
        room = self.room_repo.get_room(room_number)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with room number {room_number} not found",
            )

        self.room_repo.delete_room_in_db(room)
        return {
            "message": f"Room {room_number} deleted successfully",
            "room_number": room_number,
        }

    @handle_db_exceptions
    def get_all_rooms(self) -> List[Dict[str, Any]]:
        rooms = self.room_repo.get_all_rooms()
        return (RoomService.room_to_dict(room) for room in rooms)
