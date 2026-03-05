from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from app.services.user_service import UserService
from test.conftest import app, client


class TestLoginEndpoint:
    """Tests for POST /users/token"""

    def test_login_missing_username(self):
        """Test login with missing username"""
        response = client.post("/users/token", data={"password": "password123"})
        assert response.status_code == 422

    def test_login_missing_password(self):
        """Test login with missing password"""
        response = client.post("/users/token", data={"username": "testuser"})
        assert response.status_code == 422

    def test_login_empty_credentials(self):
        """Test login with empty username and password"""
        mock_service = Mock()
        mock_service.authenticate_user.return_value = None

        app.dependency_overrides[UserService] = lambda: mock_service

        response = client.post("/users/token", data={"username": "", "password": ""})
        assert response.status_code == 422


class TestRegisterEndpoint:
    """Tests for POST /users"""

    def test_register_missing_name(self):
        """Test registration with missing name field"""
        user_data = {
            "username": "testuser",
            "password": "password123",
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422

    def test_register_missing_username(self):
        """Test registration with missing username field"""
        user_data = {
            "name": "Test User",
            "password": "password123",
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422

    def test_register_missing_password(self):
        """Test registration with missing password field"""
        user_data = {
            "name": "Test User",
            "username": "testuser",
        }
        response = client.post("/users", json=user_data)
        assert response.status_code == 422


class TestPutRolesEndpoint:
    """Tests for PUT /users/roles"""

    def test_put_roles_missing_username(self, mock_admin_user):
        """Test role update with missing username"""
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        role_data = {"roles": ["admin"]}
        response = client.put("/users/roles", json=role_data)
        assert response.status_code == 422

    def test_put_roles_missing_roles(self, mock_admin_user):
        """Test role update with missing roles field"""
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        role_data = {"username": "testuser"}
        response = client.put("/users/roles", json=role_data)
        assert response.status_code == 422
