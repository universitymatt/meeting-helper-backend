from typing import List
from app.db.models import Role, User
from app.repositories.base_repository import BaseRepository
from app.services.exception_wrapper import handle_db_exceptions


class RoleRepository(BaseRepository):
    """Role repository containing the methods for interacting with roles in the database"""

    @handle_db_exceptions
    def get_all_roles(self) -> List[Role]:
        return self.db.query(Role).all()

    def get_role(self, role: str) -> Role:
        return self.db.query(Role).filter(Role.role == role).first()

    def update_roles(self, user: User, roles: List[Role]):
        user.roles = roles
        self.db.commit()
        return user
