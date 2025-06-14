from datetime import datetime, timedelta
import random
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Room, User, Booking, Role, user_role_table

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def seed_data_if_needed():
    """Only seeds if no users exist."""
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("Database already seeded. Skipping...")
            return
        seed_database(db, clear=True)
    finally:
        db.close()


def seed_database(db: Session = None, clear: bool = False):
    """The actual seeding logic (callable with an open db session)."""
    db = db or SessionLocal()
    try:
        if clear:
            print("Clearing existing data...")
            db.execute(user_role_table.delete())
            db.query(Booking).delete()
            db.query(User).delete()
            db.query(Room).delete()
            db.query(Role).delete()

        # Seed Roles
        roles_data = ["admin", "manager", "employee", "guest"]
        roles = [Role(role=role) for role in roles_data]
        db.add_all(roles)
        db.commit()

        # Seed Rooms
        rooms_data = [
            {
                "room_number": "A101",
                "capacity": 10,
                "description": "Small conference room with projector",
                "request_only": False,
            },
            {
                "room_number": "A102",
                "capacity": 6,
                "description": "Meeting room with whiteboard",
                "request_only": False,
            },
            {
                "room_number": "B201",
                "capacity": 20,
                "description": "Large conference room with video conferencing",
                "request_only": True,
            },
            {
                "room_number": "B202",
                "capacity": 4,
                "description": "Small huddle room",
                "request_only": False,
            },
            {
                "room_number": "C301",
                "capacity": 50,
                "description": "Main presentation hall",
                "request_only": True,
            },
            {
                "room_number": "C302",
                "capacity": 8,
                "description": "Training room with computers",
                "request_only": False,
            },
            {
                "room_number": "D401",
                "capacity": 12,
                "description": "Boardroom with executive setup",
                "request_only": True,
            },
            {
                "room_number": "D402",
                "capacity": 15,
                "description": "Workshop room with flexible seating",
                "request_only": False,
            },
        ]
        rooms = [Room(**room_data) for room_data in rooms_data]
        db.add_all(rooms)
        db.commit()

        # Seed Users
        users_data = [
            {"name": "Admin User", "username": "admin", "roles": ["admin"]},
            {
                "name": "John Manager",
                "username": "jmanager",
                "roles": ["manager", "employee"],
            },
            {"name": "Alice Smith", "username": "asmith", "roles": ["employee"]},
            {"name": "Bob Johnson", "username": "bjohnson", "roles": ["employee"]},
            {"name": "Carol Davis", "username": "cdavis", "roles": ["employee"]},
            {"name": "David Wilson", "username": "dwilson", "roles": ["employee"]},
            {
                "name": "Eva Brown",
                "username": "ebrown",
                "roles": ["manager", "employee"],
            },
            {"name": "Frank Miller", "username": "fmiller", "roles": ["employee"]},
            {"name": "Grace Lee", "username": "glee", "roles": ["employee"]},
            {"name": "Guest User", "username": "guest", "roles": ["guest"]},
        ]
        users = []
        for user_data in users_data:
            user = User(
                name=user_data["name"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["username"]),
            )
            users.append(user)
            db.add(user)
        db.commit()

        # Assign roles
        for i, user_data in enumerate(users_data):
            user = users[i]
            for role_name in user_data["roles"]:
                db.execute(
                    user_role_table.insert().values(user_id=user.id, role=role_name)
                )
        db.commit()

        # Seed Bookings
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        bookings_data = [
            {"user_idx": 1, "room": "A101", "start_offset": 0, "duration": 2},
            {"user_idx": 2, "room": "A102", "start_offset": 1, "duration": 1},
            {"user_idx": 3, "room": "B201", "start_offset": 3, "duration": 3},
            {"user_idx": 4, "room": "C302", "start_offset": 5, "duration": 2},
            {"user_idx": 5, "room": "A101", "start_offset": 24, "duration": 1},
            {"user_idx": 6, "room": "B202", "start_offset": 26, "duration": 2},
            {"user_idx": 7, "room": "D401", "start_offset": 28, "duration": 4},
            {"user_idx": 1, "room": "C301", "start_offset": 48, "duration": 6},
            {"user_idx": 8, "room": "A102", "start_offset": 50, "duration": 2},
            {"user_idx": 2, "room": "D402", "start_offset": 168, "duration": 3},
            {"user_idx": 3, "room": "B201", "start_offset": 192, "duration": 4},
        ]

        for bd in bookings_data:
            start_time = base_date + timedelta(hours=bd["start_offset"])
            end_time = start_time + timedelta(hours=bd["duration"])
            booking = Booking(
                user_id=users[bd["user_idx"]].id,
                room_number=bd["room"],
                start_time=start_time,
                end_time=end_time,
                datetime_made=datetime.now(),
            )
            db.add(booking)
        db.commit()

        # Additional random bookings
        for _ in range(15):
            user = random.choice(users[1:8])
            room = random.choice(rooms)
            days_ahead = random.randint(1, 30)
            hour = random.randint(8, 16)
            duration = random.randint(1, 4)
            start_time = base_date + timedelta(days=days_ahead, hours=hour - 9)
            end_time = start_time + timedelta(hours=duration)
            booking = Booking(
                user_id=user.id,
                room_number=room.room_number,
                start_time=start_time,
                end_time=end_time,
                datetime_made=datetime.now(),
            )
            db.add(booking)
        db.commit()

        print("Database seeded.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        if not db:
            db.close()


# For CLI usage
if __name__ == "__main__":
    print("Seeding database...")
    seed_database(clear=True)
    print("Done.")
