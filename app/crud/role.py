from typing import List
from sqlalchemy.orm import Session
from app.db.models import Role, User

def get_all_roles(db: Session) -> List[Role]:
  return db.query(Role).all()

def get_role(db: Session, role: str) -> Role:
  return db.query(Role).filter(Role.role == role).first()

def update_roles(db: Session, user: User, roles: List[Role]):
    user.roles = roles
    db.commit()
    return user