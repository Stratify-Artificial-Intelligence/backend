from app.enums import ChatMessageSenderEnum, BusinessStageEnum, CurrencyUnitEnum

from pydantic import BaseModel, ConfigDict

from datetime import datetime


class BusinessBase(BaseModel):
    name: str
    location: str
    description: str | None = None
    stage: BusinessStageEnum


class Business(BusinessBase):
    goal: str | None = None
    team_size: int | None = None
    team_description: str | None = None
    user_id: int

    model_config = ConfigDict(extra='forbid')


class BusinessIdeaBase(Business):
    competitor_existence: bool | None = None
    competitor_differentiation: str | None = None
    investment: float | None = None
    investment_currency: CurrencyUnitEnum | None = None


class BusinessIdea(BusinessIdeaBase):
    id: int


class EstablishedBusinessBase(Business):
    billing: float | None = None
    billing_currency: CurrencyUnitEnum | None = None
    ebitda: float | None = None
    ebitda_currency: CurrencyUnitEnum | None = None
    profit_margin: float | None = None


class EstablishedBusiness(EstablishedBusinessBase):
    id: int
