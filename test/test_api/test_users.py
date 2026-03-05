from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from app.services.user_service import UserService
from test.conftest import app, client


class TestLoginEndpoint:
    """Tests for POST /users/token"""

    def test_login_success(self, mock_user):
        """Test successful login"""
        mock_service = Mock()
        mock_service.authenticate_user.return_value = mock_user

        app.dependency_overrides[UserService] = lambda: mock_service

        with patch.object(UserService, "create_token", return_value="fake_token"):
            response = client.post(
                "/users/token", data={"username": "testuser", "password": "password123"}
            )

        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert "access_token" in response.cookies
        mock_service.authenticate_user.assert_called_once_with(
            "testuser", "password123"
        )

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        mock_service = Mock()
        mock_service.authenticate_user.return_value = None

        app.dependency_overrides[UserService] = lambda: mock_service

        response = client.post(
            "/users/token", data={"username": "testuser", "password": "wrongpassword"}
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect username or password"
        mock_service.authenticate_user.assert_called_once_with(
            "testuser", "wrongpassword"
        )

    def test_login_sets_cookie(self, mock_user):
        """Test that login sets the access token cookie"""
        mock_service = Mock()
        mock_service.authenticate_user.return_value = mock_user

        app.dependency_overrides[UserService] = lambda: mock_service

        with patch.object(UserService, "create_token", return_value="fake_token"):
            response = client.post(
                "/users/token", data={"username": "testuser", "password": "password123"}
            )

        assert "access_token" in response.cookies
        assert response.cookies["access_token"] == '"bearer fake_token"'

    def test_login_account_locked(self):
        """Test login when account is locked due to too many failed attempts"""
        mock_service = Mock()
        mock_service.authenticate_user.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked due to too many failed attempts. Try again later",
        )

        app.dependency_overrides[UserService] = lambda: mock_service

        response = client.post(
            "/users/token", data={"username": "testuser", "password": "password123"}
        )

        assert response.status_code == 403
        assert "locked" in response.json()["detail"].lower()

    def test_login_service_error(self):
        """Test login when service raises unexpected error"""
        mock_service = Mock()
        mock_service.authenticate_user.side_effect = Exception("Unexpected error")

        app.dependency_overrides[UserService] = lambda: mock_service

        response = client.post(
            "/users/token", data={"username": "testuser", "password": "password123"}
        )
        assert response.status_code == 500


class TestRegisterEndpoint:
    """Tests for POST /users"""

    def test_register_success(self, mock_user):
        """Test successful user registration"""
        mock_service = Mock()
        mock_service.get_user_by_username.return_value = None
        mock_service.hash_password.return_value = "hashed_password"
        mock_service.create_user.return_value = mock_user

        app.dependency_overrides[UserService] = lambda: mock_service

        with patch.object(UserService, "create_token", return_value="fake_token"):
            user_data = {
                "name": "Test User",
                "username": "testuser",
                "password": "password123",
            }
            response = client.post("/users", json=user_data)

        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert "access_token" in response.cookies
        mock_service.create_user.assert_called_once()

    def test_register_username_exists(self, mock_user):
        """Test registration with existing username"""
        mock_service = Mock()
        mock_service.get_user_by_username.return_value = mock_user

        app.dependency_overrides[UserService] = lambda: mock_service

        user_data = {
            "name": "Test User",
            "username": "testuser",
            "password": "password123",
        }
        response = client.post("/users", json=user_data)

        assert response.status_code == 400
        assert response.json()["detail"] == "Username already registered"

    def test_register_sets_cookie(self, mock_user):
        """Test that registration sets the access token cookie"""
        mock_service = Mock()
        mock_service.get_user_by_username.return_value = None
        mock_service.hash_password.return_value = "hashed_password"
        mock_service.create_user.return_value = mock_user

        app.dependency_overrides[UserService] = lambda: mock_service

        with patch.object(UserService, "create_token", return_value="fake_token"):
            user_data = {
                "name": "Test User",
                "username": "testuser",
                "password": "password123",
            }
            response = client.post("/users", json=user_data)

        assert "access_token" in response.cookies
        assert response.cookies["access_token"] == '"bearer fake_token"'

    def test_register_service_error(self):
        """Test registration when service raises unexpected error"""
        mock_service = Mock()
        mock_service.get_user_by_username.return_value = None
        mock_service.create_user.side_effect = Exception("Database error")

        app.dependency_overrides[UserService] = lambda: mock_service

        user_data = {
            "name": "Test User",
            "username": "testuser",
            "password": "password123",
        }
        response = client.post("/users", json=user_data)

        assert response.status_code == 500


class TestGetMeEndpoint:
    """Tests for GET /users/me"""

    def test_get_me_success(self, mock_user):
        """Test successful get current user"""
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get("/users/me")

        assert response.status_code == 200
        assert response.json()["username"] == "testuser"

    def test_get_me_unauthorized(self):
        """Test get current user when unauthorized"""
        from app.api.dependencies import get_current_user

        def mock_unauthorized():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        app.dependency_overrides[get_current_user] = mock_unauthorized

        response = client.get("/users/me")

        assert response.status_code == 401

    def test_get_me_returns_correct_fields(self, mock_user):
        """Test that get me returns expected user fields"""
        from app.api.dependencies import get_current_user

        app.dependency_overrides[get_current_user] = lambda: mock_user

        response = client.get("/users/me")

        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "name" in data
        assert "hashed_password" not in data


class TestGetAllUsersEndpoint:
    """Tests for GET /users/all"""

    def test_get_all_users_success(self, mock_admin_user, mock_user):
        """Test successful get all users by admin"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.get_all_users_from_db.return_value = [mock_user, mock_admin_user]

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.get("/users/all")

        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_service.get_all_users_from_db.assert_called_once()

    def test_get_all_users_error(self, mock_admin_user):
        """Test get all users with database error"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.get_all_users_from_db.side_effect = Exception("Database error")

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.get("/users/all")

        assert response.status_code == 500
        assert response.json()["detail"] == "Error retrieving users"

    def test_get_all_users_empty(self, mock_admin_user):
        """Test get all users when no users exist"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.get_all_users_from_db.return_value = []

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        response = client.get("/users/all")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_users_unauthorized(self):
        """Test get all users when not authenticated"""
        from app.api.dependencies import get_current_user

        def mock_unauthorized():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        app.dependency_overrides[get_current_user] = mock_unauthorized

        response = client.get("/users/all")

        assert response.status_code == 401

    def test_get_all_users_forbidden(self, mock_user):
        """Test get all users when user does not have admin role"""
        from app.api.dependencies import get_current_user

        def mock_forbidden():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        app.dependency_overrides[get_current_user] = mock_forbidden

        response = client.get("/users/all")

        assert response.status_code == 403


class TestLogoutEndpoint:
    """Tests for POST /users/logout"""

    def test_logout_success(self):
        """Test successful logout"""
        response = client.post("/users/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
        assert response.cookies.get("access_token") is None

    def test_logout_clears_cookie(self):
        """Test that logout properly clears the access token cookie"""
        response = client.post("/users/logout")

        assert response.status_code == 200
        assert response.cookies.get("access_token") is None

    def test_logout_when_not_logged_in(self):
        """Test logout when no session exists - should still return 200"""
        response = client.post("/users/logout")
        assert response.status_code == 200


class TestPutRolesEndpoint:
    """Tests for PUT /users/roles"""

    def test_put_roles_success(self, mock_admin_user, mock_user):
        """Test successful role update by admin"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_user.role_names = ["admin", "user"]
        mock_service.put_roles.return_value = mock_user

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        role_data = {"username": "testuser", "roles": ["admin", "user"]}
        response = client.put("/users/roles", json=role_data)

        assert response.status_code == 200
        assert (
            "Roles ['admin', 'user'] updated for user testuser"
            in response.json()["message"]
        )
        mock_service.put_roles.assert_called_once()

    def test_put_roles_error(self, mock_admin_user):
        """Test role update with service error"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.put_roles.side_effect = Exception("Database error")

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        role_data = {"username": "testuser", "roles": ["admin"]}
        response = client.put("/users/roles", json=role_data)

        assert response.status_code == 500
        assert response.json()["detail"] == "Error updating user roles"

    def test_put_roles_user_not_found(self, mock_admin_user):
        """Test role update when target user does not exist"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.put_roles.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        role_data = {"username": "nonexistent", "roles": ["admin"]}
        response = client.put("/users/roles", json=role_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_put_roles_invalid_role(self, mock_admin_user):
        """Test role update with a role that does not exist"""
        from app.api.dependencies import get_current_user

        mock_service = Mock()
        mock_service.put_roles.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role 'superuser' not found"
        )

        app.dependency_overrides[UserService] = lambda: mock_service
        app.dependency_overrides[get_current_user] = lambda: mock_admin_user

        role_data = {"username": "testuser", "roles": ["superuser"]}
        response = client.put("/users/roles", json=role_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_put_roles_unauthorized(self):
        """Test role update when not authenticated"""
        from app.api.dependencies import get_current_user

        def mock_unauthorized():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        app.dependency_overrides[get_current_user] = mock_unauthorized

        role_data = {"username": "testuser", "roles": ["admin"]}
        response = client.put("/users/roles", json=role_data)

        assert response.status_code == 401
