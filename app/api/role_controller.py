from fastapi import APIRouter, Depends
from app.api.dependencies import require_role
from app.db.models import User
from app.repositories.role_repository import RoleRepository
import logging

logger = logging.getLogger("app.roles")

role_router = APIRouter(prefix="/roles", tags=["Roles"])


@role_router.get("")
def get_all_roles(
    _: User = Depends(require_role(["admin"])), role_repo: RoleRepository = Depends()
):
    return role_repo.get_all_roles()
