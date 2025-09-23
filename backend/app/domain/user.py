from pydantic import BaseModel, ConfigDict

from app.enums import UserLanguageEnum, UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool
    role: UserRoleEnum
    language: UserLanguageEnum
    payment_service_user_id: str | None = None
    plan_id: int | None = None
    available_credits: int | None = None

    model_config = ConfigDict(from_attributes=True)


class UserWithSecret(UserBase):
    external_id: str | None = None


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserExtended(User, UserWithSecret):
    pass
