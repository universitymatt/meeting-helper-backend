import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate, UserOut, PutRoles


class TestUserCreate:
    """Test the UserCreate schema"""

    def test_valid_user_create(self):
        """Test valid user creation"""
        user = UserCreate(
            username="testuser", password="testpassword", name="Test User"
        )

        assert user.username == "testuser"
        assert user.password == "testpassword"
        assert user.name == "Test User"

    def test_required_fields(self):
        """Test that all fields are required"""
        with pytest.raises(ValidationError):
            UserCreate()

        with pytest.raises(ValidationError):
            UserCreate(username="test")

        with pytest.raises(ValidationError):
            UserCreate(username="test", password="pass")

        with pytest.raises(ValidationError):
            UserCreate(password="pass", name="Test")

    def test_empty_strings(self):
        """Test that empty strings are validated"""
        with pytest.raises(ValidationError):
            UserCreate(username="", password="pass", name="Test")

        with pytest.raises(ValidationError):
            UserCreate(username="test", password="", name="Test")

        with pytest.raises(ValidationError):
            UserCreate(username="test", password="pass", name="")


class TestUserOut:
    """Test the UserOut schema"""

    def test_valid_user_out(self):
        """Test valid UserOut creation"""
        user_data = {
            "name": "Test User",
            "username": "testuser",
            "role_names": ["admin", "user"],
        }

        user = UserOut(**user_data)

        assert user.name == "Test User"
        assert user.username == "testuser"
        assert user.role_names == ["admin", "user"]

    def test_empty_roles_list(self):
        """Test that empty roles list is allowed"""
        user_data = {"name": "Test User", "username": "testuser", "role_names": []}

        user = UserOut(**user_data)
        assert user.role_names == []

    def test_required_fields(self):
        """Test that all fields are required"""
        with pytest.raises(ValidationError):
            UserOut()

        with pytest.raises(ValidationError):
            UserOut(name="Test")

        with pytest.raises(ValidationError):
            UserOut(name="Test", username="test")


class TestPutRoles:
    """Test the PutRoles schema"""

    def test_valid_put_roles(self):
        """Test valid PutRoles creation"""
        put_roles = PutRoles(username="testuser", roles=["admin", "teacher", "user"])

        assert put_roles.username == "testuser"
        assert put_roles.roles == ["admin", "teacher", "user"]

    def test_empty_roles_list(self):
        """Test that empty roles list is allowed"""
        put_roles = PutRoles(username="testuser", roles=[])

        assert put_roles.roles == []

    def test_single_role(self):
        """Test that single role works"""
        put_roles = PutRoles(username="testuser", roles=["admin"])

        assert put_roles.roles == ["admin"]

    def test_required_fields(self):
        """Test that both fields are required"""
        with pytest.raises(ValidationError):
            PutRoles()

        with pytest.raises(ValidationError):
            PutRoles(username="test")

        with pytest.raises(ValidationError):
            PutRoles(roles=["admin"])

    def test_empty_username(self):
        """Test that empty username raises ValidationError"""
        with pytest.raises(ValidationError):
            PutRoles(username="", roles=["admin"])
