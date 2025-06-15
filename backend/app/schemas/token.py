from pydantic import BaseModel


class TokenData(BaseModel):
    sub: str

    @property
    def user_external_id(self) -> str:
        """Return the user external ID."""
        return self.sub
