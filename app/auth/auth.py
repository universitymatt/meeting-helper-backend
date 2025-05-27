from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from pytz import timezone

from app.crud.user import get_user_by_username
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_SECONDS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone("Europe/London")) + (expires_delta or timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)


