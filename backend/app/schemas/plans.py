from pydantic import BaseModel, ConfigDict


class PlanBase(BaseModel):
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Plan(PlanBase):
    id: int | None = None
