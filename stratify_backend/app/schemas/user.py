from pydantic import BaseModel, ConfigDict, SecretStr

from app.enums import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool
    role: UserRoleEnum

    model_config = ConfigDict(extra='forbid')


class User(UserBase):
    id: int


class Password(SecretStr):
    min_length = 6
    max_length = 50


class UserCreate(UserBase):
    password: Password
