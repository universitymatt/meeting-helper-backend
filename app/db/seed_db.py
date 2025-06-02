from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random
from passlib.context import CryptContext
from app.db.database import engine, SessionLocal
from app.db.models import Room, User, Booking, Role, user_role_table

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# Import your models - adjust these import paths as needed

# Or create session if not imported
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_database():
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - remove if you want to keep existing data)
        print("Clearing existing data...")
        # Clear the association table first
        db.execute(user_role_table.delete())
        db.query(Booking).delete()
        db.query(User).delete()
        db.query(Room).delete()
        db.query(Role).delete()
        
        # Seed Roles
        print("Creating roles...")
        roles_data = [
            "admin",
            "manager", 
            "employee",
            "guest"
        ]
        
        roles = []
        for role_name in roles_data:
            role = Role(role=role_name)
            roles.append(role)
            db.add(role)
        
        db.commit()
        
        # Seed Rooms
        print("Creating rooms...")
        rooms_data = [
            {"room_number": "A101", "capacity": 10, "description": "Small conference room with projector", "request_only": False},
            {"room_number": "A102", "capacity": 6, "description": "Meeting room with whiteboard", "request_only": False},
            {"room_number": "B201", "capacity": 20, "description": "Large conference room with video conferencing", "request_only": True},
            {"room_number": "B202", "capacity": 4, "description": "Small huddle room", "request_only": False},
            {"room_number": "C301", "capacity": 50, "description": "Main presentation hall", "request_only": True},
            {"room_number": "C302", "capacity": 8, "description": "Training room with computers", "request_only": False},
            {"room_number": "D401", "capacity": 12, "description": "Boardroom with executive setup", "request_only": True},
            {"room_number": "D402", "capacity": 15, "description": "Workshop room with flexible seating", "request_only": False},
        ]
        
        rooms = []
        for room_data in rooms_data:
            room = Room(**room_data)
            rooms.append(room)
            db.add(room)
        
        db.commit()
        
        # Seed Users
        print("Creating users...")
        users_data = [
            {"name": "Admin User", "username": "admin", "roles": ["admin"]},
            {"name": "John Manager", "username": "jmanager", "roles": ["manager", "employee"]},
            {"name": "Alice Smith", "username": "asmith", "roles": ["employee"]},
            {"name": "Bob Johnson", "username": "bjohnson", "roles": ["employee"]},
            {"name": "Carol Davis", "username": "cdavis", "roles": ["employee"]},
            {"name": "David Wilson", "username": "dwilson", "roles": ["employee"]},
            {"name": "Eva Brown", "username": "ebrown", "roles": ["manager", "employee"]},
            {"name": "Frank Miller", "username": "fmiller", "roles": ["employee"]},
            {"name": "Grace Lee", "username": "glee", "roles": ["employee"]},
            {"name": "Guest User", "username": "guest", "roles": ["guest"]},
        ]
        
        users = []
        for user_data in users_data:
            # Create user with hashed password (using username as password for demo)
            user = User(
                name=user_data["name"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["username"])  # Simple demo password
            )
            users.append(user)
            db.add(user)
        
        db.commit()
        
        # Assign roles to users using the association table
        print("Assigning roles to users...")
        for i, user_data in enumerate(users_data):
            user = users[i]
            for role_name in user_data["roles"]:
                # Insert into association table
                stmt = user_role_table.insert().values(user_id=user.id, role=role_name)
                db.execute(stmt)
        
        db.commit()
        
        # Seed Bookings
        print("Creating sample bookings...")
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        bookings_data = [
            # Today's bookings
            {"user_idx": 1, "room": "A101", "start_offset": 0, "duration": 2},  # 9-11 AM
            {"user_idx": 2, "room": "A102", "start_offset": 1, "duration": 1},  # 10-11 AM
            {"user_idx": 3, "room": "B201", "start_offset": 3, "duration": 3},  # 12-3 PM
            {"user_idx": 4, "room": "C302", "start_offset": 5, "duration": 2},  # 2-4 PM
            
            # Tomorrow's bookings
            {"user_idx": 5, "room": "A101", "start_offset": 24, "duration": 1},  # Tomorrow 9-10 AM
            {"user_idx": 6, "room": "B202", "start_offset": 26, "duration": 2},  # Tomorrow 11 AM-1 PM
            {"user_idx": 7, "room": "D401", "start_offset": 28, "duration": 4},  # Tomorrow 1-5 PM
            
            # Day after tomorrow
            {"user_idx": 1, "room": "C301", "start_offset": 48, "duration": 6},  # Day after 9 AM-3 PM
            {"user_idx": 8, "room": "A102", "start_offset": 50, "duration": 2},  # Day after 11 AM-1 PM
            
            # Next week bookings
            {"user_idx": 2, "room": "D402", "start_offset": 168, "duration": 3},  # Next week Monday
            {"user_idx": 3, "room": "B201", "start_offset": 192, "duration": 4},  # Next week Tuesday
        ]
        
        for booking_data in bookings_data:
            start_time = base_date + timedelta(hours=booking_data["start_offset"])
            end_time = start_time + timedelta(hours=booking_data["duration"])
            
            booking = Booking(
                user_id=users[booking_data["user_idx"]].id,
                room_number=booking_data["room"],
                start_time=start_time,
                end_time=end_time
            )
            db.add(booking)
        
        db.commit()
        
        # Add some random future bookings
        print("Creating additional random bookings...")
        for _ in range(15):
            user = random.choice(users[1:8])  # Don't use admin or guest for random bookings
            room = random.choice(rooms)
            
            # Random date in next 30 days
            days_ahead = random.randint(1, 30)
            hour = random.randint(8, 16)  # 8 AM to 4 PM
            duration = random.randint(1, 4)  # 1-4 hours
            
            start_time = base_date + timedelta(days=days_ahead, hours=hour-9)
            end_time = start_time + timedelta(hours=duration)
            
            booking = Booking(
                user_id=user.id,
                room_number=room.room_number,
                start_time=start_time,
                end_time=end_time
            )
            db.add(booking)
        
        db.commit()
        
        print("Database seeded successfully!")
        print(f"Created:")
        print(f"  - {len(roles)} roles")
        print(f"  - {len(rooms)} rooms") 
        print(f"  - {len(users)} users")
        print(f"  - {db.query(Booking).count()} bookings")
        print(f"  - {len(db.execute(user_role_table.select()).fetchall())} role assignments")
        
        # Print some sample login info
        print("\nSample login credentials (username/password):")
        print("  - admin/admin (Admin)")
        print("  - jmanager/jmanager (Manager)")
        print("  - asmith/asmith (Employee)")
        print("  - guest/guest (Guest)")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database seeding...")
    seed_database()
    print("Seeding completed!")