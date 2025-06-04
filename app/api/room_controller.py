from app.auth.utils import require_role
from app.crud.role import get_role
from app.crud.room import convert_times, create_room_in_db, delete_room_in_db, get_available_rooms_capacity, get_available_rooms_time, get_room
from app.api.get_db import get_db
from app.auth.utils import get_current_user
from app.db.models import Room, User
from app.schemas.room import GetRooms, RoomCreate
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

@room_router.get("")
def get_available_rooms(room: GetRooms = Depends(), _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # get available rooms
    if room.start_datestr and room.end_datestr:
        # check times are valid
        valid_times = convert_times(room.start_datestr, room.end_datestr)
        available_rooms = get_available_rooms_time(db, room.min_capacity, valid_times["start_datetime"], valid_times["end_datetime"])
    else:
        # get rooms based on time and capacity = 0
        available_rooms = get_available_rooms_capacity(db, room.min_capacity)
    return {
        "filters": room,
        "rooms": available_rooms
    }
    
    
@room_router.post("")
def create_room(room: RoomCreate, _: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    # check the room doesn't exist
    if get_room(db, room.room_number):
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Room with room number {room.room_number} already exists")
    # get the roles
    role_list = []
    if room.roles:
        for role_name in room.roles:
            role = get_role(db, role_name)
            if not role:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_name}' not found")
            role_list.append(role)
    new_room = Room(
        room_number = room.room_number,
        capacity = room.capacity,
        description = room.description,
        request_only = room.request_only,
        allowed_roles = role_list,
    )
    new_room = create_room_in_db(db, new_room)
    return new_room

@room_router.delete("/{room_number}")
def delete_room(room_number: str, _: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    room = get_room(db, room_number)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with room number {room_number} not found")
    
    try: 
        delete_room_in_db(db, room)
        return {"message": f"Room {room_number} deleted successfully", "room_number": room_number}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error occurred deleting Room {room_number}")