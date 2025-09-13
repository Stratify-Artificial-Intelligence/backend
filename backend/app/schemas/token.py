from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = ConfigDict(extra='forbid')


class TokenData(BaseModel):
    sub: str
    impersonated_sub: str | None = None

    @property
    def user_external_id(self) -> str:
        """Return the user external ID."""
        return self.sub

    @property
    def impersonated_user_external_id(self) -> str | None:
        """Return the impersonated user external ID, if any"""
        return self.impersonated_sub

    @property
    def is_impersonation(self) -> bool:
        """Return True if the token is an impersonation token."""
        return self.impersonated_sub is not None
