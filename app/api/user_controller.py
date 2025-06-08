from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from app.api.dependencies import get_current_user, require_role
from app.db.models import User
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.user import PutRoles, UserCreate, UserOut
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/token", response_model=UserOut)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
):
    logger.info(f"Login attempt for username: {form_data.username}")

    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    logger.info(f"Successful login for user: {user.username}")
    access_token = UserService.create_token(user_data={"username": user.username})

    # set access token in http cookie rather than returning in response
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}",
        httponly=True,
        samesite="none",
        secure=True,
        max_age=60 * 60 * 24,
    )
    return UserOut.model_validate(user)


@user_router.post("", response_model=UserOut)
def register_user(
    response: Response,
    user: UserCreate,
    user_service: UserService = Depends(),
):
    logger.info(f"User registration attempt for username: {user.username}")

    db_user = user_service.get_user_by_username(user.username)
    if db_user:
        logger.warning(
            f"Registration failed - username already exists: {user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    try:
        new_user = User(
            name=user.name,
            username=user.username,
            hashed_password=user_service.hash_password(user.password),
        )
        created_user = user_service.create_user(new_user)
        logger.info(f"Successfully registered user: {created_user.username}")

        access_token = UserService.create_token(
            user_data={"username": created_user.username}
        )
        response.set_cookie(
            key="access_token",
            value=f"bearer {access_token}",
            httponly=True,
            samesite="none",
            secure=True,
            max_age=60 * 60 * 24,
        )
        return UserOut.model_validate(created_user)
    except Exception as e:
        logger.error(f"Error creating user {user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )


@user_router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    logger.debug(f"User profile requested by: {current_user.username}")
    return UserOut.model_validate(current_user)


@user_router.get("/all", response_model=List[UserOut])
def get_all_users(
    current_admin: User = Depends(require_role(["admin"])),
    user_service: UserService = Depends(),
):
    logger.info(f"All users requested by admin: {current_admin.username}")

    try:
        users = user_service.get_all_users_from_db()
        logger.debug(f"Retrieved {len(users)} users from database")
        return [UserOut.model_validate(user) for user in users]
    except Exception as e:
        logger.error(f"Error retrieving all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users",
        )


@user_router.post("/logout")
def logout(response: Response):
    logger.info("User logout requested")

    # clear access token in cookie
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        samesite="none",
        secure=True,
        expires=0,
    )
    logger.info("User logged out successfully")
    return {"message": "Logged out successfully"}


@user_router.put("/roles")
def put_roles(
    user_roles: PutRoles,
    user_service: UserService = Depends(),
    current_admin: User = Depends(require_role(["admin"])),
):
    logger.info(
        f"Role update requested by admin {current_admin.username} for user {user_roles.username}"
    )

    try:
        user = user_service.put_roles(user_roles)
        logger.info(
            f"Successfully updated roles for user {user.username}: {user.role_names}"
        )
        return {"message": f"Roles {user.role_names} updated for user {user.username}"}
    except Exception as e:
        logger.error(f"Error updating roles for user {user_roles.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user roles",
        )
