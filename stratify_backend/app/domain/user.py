from pydantic import BaseModel, ConfigDict

from app.enums import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool
    password: str
    role: UserRoleEnum

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
