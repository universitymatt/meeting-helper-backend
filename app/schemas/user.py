from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    name: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True