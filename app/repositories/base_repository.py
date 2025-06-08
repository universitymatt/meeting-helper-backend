from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BaseRepository:
    """Base repository class containing db connection"""

    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
