from datetime import datetime, timedelta
from typing import List
import uuid
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from app.auth.oauth_password_bearer import OAuth2PasswordBearerWithCookie
from app.db.models import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
import app.config as Config
import jwt

from app.schemas.user import PutRoles
from app.services.exception_wrapper import handle_db_exceptions

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")


class UserService:
    """Service injects repositories (which contains DB connections)"""

    def __init__(
        self,
        user_repo: UserRepository = Depends(),
        role_repo: RoleRepository = Depends(),
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def get_username_from_jwt(token: str) -> str:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        user = payload.get("user")
        username = user.get("username")
        return username

    @staticmethod
    def create_token(user_data: dict, expiry: timedelta = None):
        payload = {}
        payload["user"] = user_data
        payload["exp"] = datetime.now() + (
            expiry
            if expiry is not None
            else timedelta(seconds=Config.ACCESS_TOKEN_EXPIRE_SECONDS)
        )
        payload["jti"] = str(uuid.uuid4())
        token = jwt.encode(
            payload=payload, key=Config.SECRET_KEY, algorithm=Config.ALGORITHM
        )

        if isinstance(token, bytes):
            token = token.decode("utf-8")

        return token

    @handle_db_exceptions
    def authenticate_user(self, username: str, password: str):
        user = self.user_repo.get_user_by_username(username)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        return user

    @handle_db_exceptions
    def create_user(self, user: User):
        return self.user_repo.create_user(user)

    @handle_db_exceptions
    def get_all_users_from_db(self) -> List[User]:
        return self.user_repo.get_all_users_from_db()

    @handle_db_exceptions
    def put_roles(self, user_roles: PutRoles) -> User:
        user = self.user_repo.get_user_by_username(user_roles.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        role_list = []
        for role_name in user_roles.roles:
            role = self.role_repo.get_role(role_name)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Role '{role_name}' not found",
                )
            role_list.append(role)

        return self.role_repo.update_roles(user, role_list)
