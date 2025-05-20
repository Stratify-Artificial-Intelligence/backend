from pydantic import BaseModel, ConfigDict


class Plan(BaseModel):
    id: int | None = None
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
