from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from unittest.mock import Mock
from app.db.models import User
from app.api.booking_controller import booking_router
from app.api.room_controller import room_router
from app.api.user_controller import user_router
from app.api.role_controller import role_router

app = FastAPI()
app.include_router(booking_router)
app.include_router(room_router)
app.include_router(user_router)
app.include_router(role_router)
client = TestClient(app)


@pytest.fixture
def mock_user():
    """Mock user object for testing"""
    user = Mock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.name = "Test User"
    user.role_names = ["user"]
    return user


@pytest.fixture
def mock_admin_user():
    """Mock admin user object for testing"""
    user = Mock(spec=User)
    user.id = 2
    user.username = "admin"
    user.name = "Admin User"
    user.role_names = ["admin"]
    return user


@pytest.fixture
def mock_booking():
    """Mock booking object for testing"""
    return {
        "id": 1,
        "room_number": "101",
        "user_id": 1,
        "start_datetime": "2026-08-01T10:00:00",
        "end_datetime": "2026-08-01T12:00:00",
    }


@pytest.fixture
def mock_room_data():
    """Mock room data for testing"""
    return {
        "room_number": "101",
        "capacity": 10,
        "sufficient_roles": True,
        "location": "Building A",
    }
