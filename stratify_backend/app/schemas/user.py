from pydantic import BaseModel, ConfigDict, SecretStr


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool

    model_config = ConfigDict(extra='forbid')


class User(UserBase):
    id: int


class Password(SecretStr):
    min_length = 6
    max_length = 50


class UserCreate(UserBase):
    password: Password
