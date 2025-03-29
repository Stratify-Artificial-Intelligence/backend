from pydantic import BaseModel, ConfigDict

from app.enums import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool
    role: UserRoleEnum

    model_config = ConfigDict(from_attributes=True)


class UserWithSecret(UserBase):
    password: str


class User(UserWithSecret):
    id: int

    model_config = ConfigDict(from_attributes=True)
