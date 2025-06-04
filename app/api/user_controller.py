from typing import List
from app.api.get_db import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils import authenticate_user, create_token, get_current_user, require_role
from app.auth.password import hash_password
from app.crud.role import get_role, update_roles
from app.crud.user import create_user, get_all_users_from_db, get_user_by_username
from app.db.models import User
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.user import PutRoles, UserCreate, UserOut


user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/token", response_model=UserOut)
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = create_token(user_data={"username": user.username})

    # set access token in http cookie rather than returning in response
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}", 
        httponly=True,
        samesite="none",
        secure=True,
        max_age=60 * 60 * 24
    )
    return UserOut.model_validate(user)

    
@user_router.post("", response_model=UserOut)
def register_user(response: Response, user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    user = User(
        name=user.name,
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    user = create_user(db, user)
    access_token = create_token(user_data={"username": user.username})
    response.set_cookie(
        key="access_token",
        value=f"bearer {access_token}", 
        httponly=True,
        samesite="none",
        secure=True,
        max_age=60 * 60 * 24
    )
    return UserOut.model_validate(user)


@user_router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)

@user_router.get("/all", response_model=List[UserOut])
def get_all_users(_: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    users = get_all_users_from_db(db)
    return [UserOut.model_validate(user) for user in users]


@user_router.post("/logout")
def logout(response: Response, db: Session = Depends(get_db)):
    # clear access token in cookie
    response.set_cookie(
        key="access_token",
        httponly=True,
        samesite="none",
        secure=True,
    )
    return {"message": "Logged out successfully"}

@user_router.put("/roles")
def put_roles(user_roles: PutRoles, db: Session = Depends(get_db), _: User = Depends(require_role(["admin"]))):
    user = get_user_by_username(db, user_roles.username)
    if not user:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    role_list = []
    for role_name in user_roles.roles:
        role = get_role(db, role_name)
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_name}' not found")
        role_list.append(role)
    
    user = update_roles(db, user, role_list)
    return {"message": f"Roles {user.role_names} updated for user {user.username}"}