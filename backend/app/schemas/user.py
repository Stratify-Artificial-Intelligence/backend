from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

from app.enums import UserLanguageEnum, UserRoleEnum


class UserBase(BaseModel):
    username: str
    email: str
    full_name: str
    language: UserLanguageEnum

    model_config = ConfigDict(extra='forbid')


class UserBaseExtended(UserBase):
    is_active: bool
    role: UserRoleEnum
    plan_id: int | None = None
    payment_service_user_id: str | None = None
    available_credits: int | None = None


class User(UserBaseExtended):
    id: int


class Password(SecretStr):
    min_length = 6
    max_length = 50


class UserSecret(BaseModel):
    password: Password | None = None
    external_id: str | None = None

    @model_validator(mode='after')
    def validate_password_xor_external_id(self):
        if not (self.password or self.external_id):
            raise ValueError('Either password or external_id must be provided.')
        if self.password and self.external_id:
            raise ValueError('Only one of password or external_id can be provided.')
        return self


class UserCreate(UserSecret, UserBaseExtended):
    pass


class UserBaseCreate(UserSecret, UserBase):
    pass


class UserMePartialUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    language: UserLanguageEnum | None = None

    model_config = ConfigDict(extra='forbid')


class UserPartialUpdate(UserMePartialUpdate):
    is_active: bool | None = None
    role: UserRoleEnum | None = None
    language: UserLanguageEnum | None = None
    plan_id: int | None = None
    payment_service_user_id: str | None = None
    available_credits: int | None = None
