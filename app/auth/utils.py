import uuid
from app.api.get_db import get_db
from app.auth.oauth_password_bearer import OAuth2PasswordBearerWithCookie
from app.auth.password import verify_password
import app.config as Config
import jwt
from fastapi import HTTPException, Depends, status
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_username
from app.db.models import User


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        username = get_username_from_jwt(token)
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired token")
    
def get_username_from_jwt(token: str) -> str:
    payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
    user = payload.get("user")
    username = user.get("username")
    return username

def create_token(user_data: dict, expiry: timedelta = None):
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=Config.ACCESS_TOKEN_EXPIRE_SECONDS))
    payload["jti"] = str(uuid.uuid4())
    token = jwt.encode(payload=payload, key=Config.SECRET_KEY, algorithm=Config.ALGORITHM)

    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return token

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def require_role(required_roles: list[str]):
    def dependency(current_user: User = Depends(get_current_user)):
        if not set(required_roles).issubset(set(current_user.role_names)):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return dependency