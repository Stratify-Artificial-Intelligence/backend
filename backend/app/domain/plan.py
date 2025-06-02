from pydantic import BaseModel, ConfigDict


class PlanBase(BaseModel):
    name: str
    is_active: bool
    price: float
    payment_service_price_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Plan(PlanBase):
    id: int
