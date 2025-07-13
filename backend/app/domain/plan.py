from pydantic import BaseModel, ConfigDict

from app.enums import UserPlanEnum


class PlanBase(BaseModel):
    name: UserPlanEnum
    is_active: bool
    price: float
    payment_service_price_id: str | None = None
    monthly_credits: int | None = None

    model_config = ConfigDict(from_attributes=True)


class Plan(PlanBase):
    id: int
