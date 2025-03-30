from pydantic import BaseModel, ConfigDict, SecretStr

from app.enums import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str

    model_config = ConfigDict(extra='forbid')


class UserBaseExtended(UserBase):
    is_active: bool
    role: UserRoleEnum


class User(UserBaseExtended):
    id: int


class Password(SecretStr):
    min_length = 6
    max_length = 50


class UserCreate(UserBaseExtended):
    password: Password


class UserBaseCreate(UserBase):
    password: Password


class UserMePartialUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None

    model_config = ConfigDict(extra='forbid')


class UserPartialUpdate(UserMePartialUpdate):
    is_active: bool | None = None
    role: UserRoleEnum | None = None
