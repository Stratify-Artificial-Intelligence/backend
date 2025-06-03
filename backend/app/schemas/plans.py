from pydantic import BaseModel, ConfigDict

from app.enums import UserPlanEnum


class PlanPartialUpdate(BaseModel):
    name: UserPlanEnum | None = None
    is_active: bool | None = None
    price: float | None = None
    payment_service_price_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PlanBase(BaseModel):
    name: UserPlanEnum
    is_active: bool
    price: float
    payment_service_price_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Plan(PlanBase):
    id: int | None = None
