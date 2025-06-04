from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserOut(BaseModel):
    name: str
    username: str
    role_names: List[str]

    class Config:
        from_attributes = True

class PutRoles(BaseModel):
    username: str
    roles: List[str]