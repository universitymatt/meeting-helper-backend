from fastapi import Depends, HTTPException, status
from app.db.models import User
from app.repositories.user_repository import UserRepository
from app.services.exception_wrapper import handle_db_exceptions
from app.services.user_service import UserService, oauth2_scheme
import jwt


@handle_db_exceptions
def get_current_user(
    token: str = Depends(oauth2_scheme), user_repo: UserRepository = Depends()
) -> User:
    try:
        username = UserService.get_username_from_jwt(token)
        user = user_repo.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user"
            )
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token"
        )


def require_role(required_roles: list[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        if not set(required_roles).issubset(set(current_user.role_names)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency
