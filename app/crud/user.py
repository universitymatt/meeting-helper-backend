from typing import List
from sqlalchemy.orm import Session
from app.db.models import User

def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_all_users_from_db(db: Session) -> List[User]:
    return db.query(User).all()