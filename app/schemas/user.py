from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserOut(BaseModel):
    name: str
    username: str
    roles: List[str]

    class Config:
        from_attributes = True 