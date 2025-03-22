from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int | None = None
    username: str
    email: str
    full_name: str
    is_active: bool
    password: str

    model_config = ConfigDict(from_attributes=True)
