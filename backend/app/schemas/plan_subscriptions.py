from pydantic import BaseModel, ConfigDict


class PlanSubscriptionResponse(BaseModel):
    id: str
    payment_client_secret: str

    model_config = ConfigDict(from_attributes=True)
