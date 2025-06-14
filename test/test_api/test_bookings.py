from unittest.mock import Mock
from app.services.booking_service import BookingService
from test.conftest import app, client


class TestCreateBookingEndpoint:
    """Tests for POST /bookings"""

    def test_create_booking_success(self, mock_user, mock_booking):
        """Test successful booking creation"""
        from app.api.dependencies import get_current_user

        # Create mock service
        mock_service = Mock(spec=BookingService)
        mock_service.booking_logic.return_value = mock_booking

        # Override dependencies
        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        booking_data = {
            "room_number": "101",
            "start_datetime": "2026-01-01T10:00:00",
            "end_datetime": "2026-01-01T12:00:00",
        }
        response = client.post("/bookings", json=booking_data)

        assert response.status_code == 200
        mock_service.booking_logic.assert_called_once()
        call_args = mock_service.booking_logic.call_args
        assert call_args[1]["is_request"] == False
        assert call_args[1]["current_user"] == mock_user


class TestCreateBookingRequestEndpoint:
    """Tests for POST /bookings/request"""

    def test_create_booking_request_success(self, mock_user, mock_booking):
        """Test successful booking request creation"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.booking_logic.return_value = mock_booking

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        booking_data = {
            "room_number": "101",
            "start_datetime": "2026-01-01T10:00:00",
            "end_datetime": "2026-01-01T12:00:00",
        }
        response = client.post("/bookings/request", json=booking_data)

        assert response.status_code == 200
        mock_service.booking_logic.assert_called_once()
        call_args = mock_service.booking_logic.call_args
        assert call_args[1]["is_request"] == True
        assert call_args[1]["current_user"] == mock_user


class TestGetBookingsEndpoint:
    """Tests for GET /bookings"""

    def test_get_bookings_success(self, mock_user, mock_booking):
        """Test successful retrieval of user bookings"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_all_your_bookings.return_value = [mock_booking]

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get("/bookings")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_service.get_all_your_bookings.assert_called_once_with(mock_user.id)

    def test_get_bookings_empty(self, mock_user):
        """Test retrieval of bookings when user has none"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_all_your_bookings.return_value = []

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get("/bookings")

        assert response.status_code == 200
        assert len(response.json()) == 0
        mock_service.get_all_your_bookings.assert_called_once_with(mock_user.id)


class TestDeleteBookingEndpoint:
    """Tests for DELETE /bookings/{booking_id}"""

    def test_delete_booking_success(self, mock_user, mock_booking):
        """Test successful booking deletion"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_your_booking.return_value = mock_booking
        mock_service.delete_booking.return_value = {
            "message": "Booking deleted successfully"
        }

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.delete("/bookings/1")

        assert response.status_code == 200
        assert "Booking deleted successfully" in response.json()["message"]
        mock_service.get_your_booking.assert_called_once_with(mock_user.id, 1)
        mock_service.delete_booking.assert_called_once_with(mock_booking)

    def test_delete_booking_not_found(self, mock_user):
        """Test deletion of non-existent or unauthorized booking"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_your_booking.return_value = None

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.delete("/bookings/999")

        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]
        mock_service.get_your_booking.assert_called_once_with(mock_user.id, 999)


class TestGetAllBookingRequestsEndpoint:
    """Tests for GET /bookings/request"""

    def test_get_all_booking_requests_success(self, mock_admin_user, mock_booking):
        """Test successful retrieval of all booking requests by admin"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_all_requests.return_value = [mock_booking]

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.get("/bookings/request")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_service.get_all_requests.assert_called_once()

    def test_get_all_booking_requests_unauthorized(self, mock_user):
        """Test booking requests retrieval by non-admin user"""
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get("/bookings/request")

        assert response.status_code == 403


class TestApproveBookingRequestEndpoint:
    """Tests for PUT /bookings/{booking_id}/approve"""

    def test_approve_booking_request_not_found(self, mock_admin_user):
        """Test approval of non-existent booking request"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_any_booking.return_value = None

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.put("/bookings/999/approve")

        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]
        mock_service.get_any_booking.assert_called_once_with(999)


class TestUpdateBookingEndpoint:
    """Tests for PUT /bookings/{booking_id}"""

    def test_update_booking_success(self, mock_user, mock_booking):
        """Test successful booking update"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_your_booking.return_value = mock_booking
        mock_service.update_booking.return_value = mock_booking

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        update_data = {
            "start_datetime": "2026-01-01T14:00:00",
            "end_datetime": "2026-01-01T16:00:00",
        }
        response = client.put("/bookings/1", json=update_data)

        assert response.status_code == 200
        mock_service.get_your_booking.assert_called_once_with(mock_user.id, 1)
        mock_service.update_booking.assert_called_once()

    def test_update_booking_not_found(self, mock_user):
        """Test update of non-existent or unauthorized booking"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_your_booking.return_value = None

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_user

        update_data = {
            "start_datetime": "2026-01-01T14:00:00",
            "end_datetime": "2026-01-01T16:00:00",
        }
        response = client.put("/bookings/999", json=update_data)

        assert response.status_code == 404
        assert "Booking 999 not found for update" in response.json()["detail"]
        mock_service.get_your_booking.assert_called_once_with(mock_user.id, 999)


class TestDeclineBookingRequestEndpoint:
    """Tests for DELETE /bookings/{booking_id}/decline"""

    def test_decline_booking_request_success(self, mock_admin_user, mock_booking):
        """Test successful booking request decline by admin"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_any_booking.return_value = mock_booking
        mock_service.delete_booking.return_value = {
            "message": "Booking request declined"
        }

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.delete("/bookings/1/decline")

        assert response.status_code == 200
        assert "Booking request declined" in response.json()["message"]
        mock_service.get_any_booking.assert_called_once_with(1)
        mock_service.delete_booking.assert_called_once_with(mock_booking)

    def test_decline_booking_request_not_found(self, mock_admin_user):
        """Test decline of non-existent booking request"""
        from app.api.dependencies import get_current_user

        mock_service = Mock(spec=BookingService)
        mock_service.get_any_booking.return_value = None

        app.dependency_overrides[BookingService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.delete("/bookings/999/decline")

        assert response.status_code == 404
        assert "Booking not found" in response.json()["detail"]
        mock_service.get_any_booking.assert_called_once_with(999)
