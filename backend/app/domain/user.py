from pydantic import BaseModel, ConfigDict

from app.enums import UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    is_active: bool
    role: UserRoleEnum
    payment_service_user_id: str | None = None
    payment_service_subscription_id: str | None = None
    plan_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class UserWithSecret(UserBase):
    password: str


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
