from pydantic import BaseModel, Field
from typing import Annotated, List


class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=1)]
    password: Annotated[str, Field(min_length=1)]
    name: Annotated[str, Field(min_length=1)]


class UserOut(BaseModel):
    name: str
    username: str
    role_names: List[str]

    class Config:
        from_attributes = True


class PutRoles(BaseModel):
    username: Annotated[str, Field(min_length=1)]
    roles: List[str]
