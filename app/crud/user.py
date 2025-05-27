from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.api.get_db import get_db
from app.db.models import User
from app.schemas.user import UserOut
from app.config import SECRET_KEY, ALGORITHM
from jose import jwt

def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        username = get_username_from_jwt(token)
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return UserOut(**user)
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    
def get_username_from_jwt(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    return username