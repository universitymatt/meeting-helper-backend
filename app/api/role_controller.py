from typing import List
from fastapi import APIRouter, Depends
from requests import Session

from app.api.get_db import get_db
from app.auth.utils import require_role
from app.crud.role import get_all_roles
from app.db.models import User

role_router = APIRouter(prefix="/roles", tags=["Roles"])

@role_router.get("")
def get_all_users(_: User = Depends(require_role(["admin"])), db: Session = Depends(get_db)):
    return get_all_roles(db)
