from pydantic import BaseModel, ConfigDict


class PaymentMethodResponse(BaseModel):
    id: str
    client_secret: str

    model_config = ConfigDict(from_attributes=True)


class PlanSubscriptionResponse(BaseModel):
    id: str
    payment_client_secret: str

    model_config = ConfigDict(from_attributes=True)
