from unittest.mock import Mock, patch
from app.services.room_service import RoomService
from test.conftest import app, client


class TestGetAvailableRoomsEndpoint:
    """Tests for GET /rooms"""

    def test_get_available_rooms_success(self, mock_user, mock_room_data):
        """Test successful retrieval of available rooms"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.get_available_rooms_time.return_value = [mock_room_data]

        app.dependency_overrides[RoomService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch.object(
            RoomService, "check_user_has_room_permissions", return_value=True
        ):
            response = client.get(
                "/rooms",
                params={
                    "min_capacity": 5,
                    "start_datetime": "2026-01-01T10:00:00",
                    "end_datetime": "2026-01-01T12:00:00",
                },
            )

        assert response.status_code == 200
        assert len(response.json()["rooms"]) == 1
        assert response.json()["rooms"][0]["room_number"] == "101"
        mock_service.get_available_rooms_time.assert_called_once()


class TestGetAllRoomsEndpoint:
    """Tests for GET /rooms/all"""

    def test_get_all_rooms_success(self, mock_user, mock_room_data):
        """Test successful retrieval of all rooms"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.get_all_rooms.return_value = [mock_room_data]

        app.dependency_overrides[RoomService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get("/rooms/all")

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["room_number"] == "101"
        mock_service.get_all_rooms.assert_called_once()


class TestCreateRoomEndpoint:
    """Tests for POST /rooms"""

    def test_create_room_success(self, mock_admin_user, mock_room_data):
        """Test successful room creation by admin"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.create_room.return_value = mock_room_data

        app.dependency_overrides[RoomService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        room_data = {"room_number": "101", "capacity": 10, "location": "Building A"}
        response = client.post("/rooms", json=room_data)

        assert response.status_code == 200
        assert response.json()["room_number"] == "101"
        mock_service.create_room.assert_called_once()

    def test_create_room_unauthorized(self, mock_user):
        """Test room creation by non-admin user"""
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_user

        room_data = {"room_number": "101", "capacity": 10, "location": "Building A"}
        response = client.post("/rooms", json=room_data)

        assert response.status_code == 403


class TestDeleteRoomEndpoint:
    """Tests for DELETE /rooms/{room_number}"""

    def test_delete_room_success(self, mock_admin_user):
        """Test successful room deletion by admin"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.delete_room.return_value = {"message": "Room deleted successfully"}

        app.dependency_overrides[RoomService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.delete("/rooms/101")

        assert response.status_code == 200
        assert "Room deleted successfully" in response.json()["message"]
        mock_service.delete_room.assert_called_once_with("101")
