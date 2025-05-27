from jose import JWTError
from app.api.get_db import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth.auth import authenticate_user, create_access_token, get_username, hash_password
from app.crud.user import create_user, get_user_by_username
from app.db.models import User
from sqlalchemy.orm import Session
from app.schemas.auth import Token
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserOut

user_router = APIRouter(prefix="/users", tags=["Users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@user_router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@user_router.get("/me", response_model=UserOut)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserOut:
    try:
        username = get_username(token)
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return UserOut(**user)
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
@user_router.post("/", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(
        name=user.name,
        username=user.username,
        hashed_password=hash_password(user.password),
    )
    user = create_user(db, user)
    return {"id": user.id, "username": user.username}