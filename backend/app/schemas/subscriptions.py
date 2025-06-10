from pydantic import BaseModel, ConfigDict


class SubscriptionCreation(BaseModel):
    plan_id: int
    success_url: str
    cancel_url: str

    model_config = ConfigDict(from_attributes=True)


class CheckoutSession(BaseModel):
    url: str

    model_config = ConfigDict(from_attributes=True)


class CheckoutSessionResponse(BaseModel):
    customer: str
    status: str
    subscription: str

    model_config = ConfigDict(from_attributes=True)


class SubscriptionHandleRequest(BaseModel):
    return_url: str

    model_config = ConfigDict(from_attributes=True)


class SubscriptionHandleResponse(BaseModel):
    url: str

    model_config = ConfigDict(from_attributes=True)


class PaymentMethodResponse(BaseModel):
    id: str
    client_secret: str

    model_config = ConfigDict(from_attributes=True)


class PlanSubscriptionResponse(BaseModel):
    id: str
    payment_client_secret: str

    model_config = ConfigDict(from_attributes=True)
