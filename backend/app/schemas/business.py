from app.enums import ChatMessageSenderEnum, BusinessStageEnum, CurrencyUnitEnum

from pydantic import BaseModel, ConfigDict

from datetime import datetime


class BusinessBase(BaseModel):
    name: str
    location: str
    description: str | None = None
    goal: str | None = None
    team_size: int | None = None
    team_description: str | None = None

    model_config = ConfigDict(extra='forbid')


class Business(BusinessBase):
    id: int
    user_id: int
    stage: BusinessStageEnum


class BusinessIdeaBase(BusinessBase):
    competitor_existence: bool | None = None
    competitor_differentiation: str | None = None
    investment: float | None = None
    investment_currency: CurrencyUnitEnum | None = None


class BusinessIdea(BusinessIdeaBase):
    id: int
    user_id: int
    stage: BusinessStageEnum


class EstablishedBusinessBase(BusinessBase):
    billing: float | None = None
    billing_currency: CurrencyUnitEnum | None = None
    ebitda: float | None = None
    ebitda_currency: CurrencyUnitEnum | None = None
    profit_margin: float | None = None


class EstablishedBusiness(EstablishedBusinessBase):
    id: int
    user_id: int
    stage: BusinessStageEnum
