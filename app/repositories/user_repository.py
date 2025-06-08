from typing import List
from app.repositories.base_repository import BaseRepository
from app.db.models import User

class UserRepository(BaseRepository):
    """User repository containing methods for interacting with users in the database"""

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_all_users_from_db(self) -> List[User]:
        return self.db.query(User).all()
    
    