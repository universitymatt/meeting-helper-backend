from app.api.get_db import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.utils import authenticate_user, create_token, get_current_user
from app.auth.password import hash_password
from app.crud.user import create_user, get_user_by_username
from app.db.models import User
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.user import UserCreate, UserOut


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
    return {"username": user.username, "name": user.name, "roles": user.role_names}
    
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
    return {"username": user.username, "name": user.name, "roles": user.roles}

@user_router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "name":current_user.name,
        "username":current_user.username,
        "roles":current_user.role_names,
    }

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