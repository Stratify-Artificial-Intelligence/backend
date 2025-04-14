from abc import ABC

from pydantic import BaseModel, ConfigDict

from app.enums import BusinessStageEnum, CurrencyUnitEnum


class Business(BaseModel, ABC):
    id: int | None = None
    name: str
    location: str
    description: str | None = None
    goal: str | None = None
    stage: BusinessStageEnum
    team_size: int | None = None
    team_description: str | None = None
    user_id: int
    user_position: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BusinessIdea(Business):
    competitor_existence: bool | None = None
    competitor_differentiation: str | None = None
    investment: float | None = None
    investment_currency: CurrencyUnitEnum | None = None


class EstablishedBusiness(Business):
    mission_and_vision: str | None = None
    billing: float | None = None
    billing_currency: CurrencyUnitEnum | None = None
    ebitda: float | None = None
    ebitda_currency: CurrencyUnitEnum | None = None
    profit_margin: float | None = None
