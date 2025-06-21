from typing import Any

from app.enums import BusinessStageEnum, CurrencyUnitEnum

from pydantic import BaseModel, ConfigDict


BUSINESS_BASE_EXAMPLE: dict[str, Any] = {
    'name': 'Veyra',
    'location': 'Spain',
    'description': 'Veyra is super cool!',
    'goal': 'Help entrepreneurs',
    'team_size': 3,
    'team_description': 'Super nice guys.',
    'user_position': 'CTO and backend developer',
    'extra_info': 'Here I could explain what the business is about',
}

BUSINESS_EXAMPLE: dict[str, Any] = {
    'id': 4,
    'user_id': 1,
    'stage': BusinessStageEnum.IDEA,
    **BUSINESS_BASE_EXAMPLE,
}

BUSINESS_IDEA_BASE_EXAMPLE: dict[str, Any] = {
    **BUSINESS_BASE_EXAMPLE,
    'competitor_existence': True,
    'competitor_differentiation': 'Well, we are the best.',
    'investment': 0,
    'investment_currency': CurrencyUnitEnum.EURO,
}

BUSINESS_IDEA_EXAMPLE: dict[str, Any] = {
    'id': 5,
    'user_id': 1,
    'stage': BusinessStageEnum.IDEA,
    **BUSINESS_IDEA_BASE_EXAMPLE,
}

ESTABLISHED_BUSINESS_BASE_EXAMPLE: dict[str, Any] = {
    **BUSINESS_BASE_EXAMPLE,
    'mission_and_vision': 'We try to be the best in class.',
    'billing': 1000,
    'billing_currency': CurrencyUnitEnum.EURO,
    'ebitda': 50,
    'ebitda_currency': CurrencyUnitEnum.EURO,
    'profit_margin': 5,
}

ESTABLISHED_BUSINESS_EXAMPLE: dict[str, Any] = {
    'id': 6,
    'user_id': 1,
    'stage': BusinessStageEnum.ESTABLISHED,
    **ESTABLISHED_BUSINESS_BASE_EXAMPLE,
}


class BusinessBaseOptional(BaseModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    goal: str | None = None
    team_size: int | None = None
    team_description: str | None = None
    user_position: str | None = None
    extra_info: str | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_BASE_EXAMPLE},
    )


class BusinessBase(BusinessBaseOptional):
    name: str
    location: str


class Business(BusinessBase):
    id: int
    user_id: int
    stage: BusinessStageEnum
    logo_url: str | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_EXAMPLE},
    )


class BusinessIdeaConcrete(BaseModel):
    competitor_existence: bool | None = None
    competitor_differentiation: str | None = None
    investment: float | None = None
    investment_currency: CurrencyUnitEnum | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_IDEA_BASE_EXAMPLE},
    )


class BusinessIdeaBase(BusinessIdeaConcrete, BusinessBase):
    pass


class BusinessIdeaPartialUpdate(BusinessIdeaConcrete, BusinessBaseOptional):
    pass


class BusinessIdea(BusinessIdeaBase):
    id: int
    user_id: int
    stage: BusinessStageEnum
    logo_url: str | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_IDEA_EXAMPLE},
    )


class EstablishedBusinessConcrete(BaseModel):
    mission_and_vision: str | None = None
    billing: float | None = None
    billing_currency: CurrencyUnitEnum | None = None
    ebitda: float | None = None
    ebitda_currency: CurrencyUnitEnum | None = None
    profit_margin: float | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': ESTABLISHED_BUSINESS_BASE_EXAMPLE},
    )


class EstablishedBusinessBase(EstablishedBusinessConcrete, BusinessBase):
    pass


class EstablishedBusinessPartialUpdate(
    EstablishedBusinessConcrete, BusinessBaseOptional
):
    pass


class EstablishedBusiness(EstablishedBusinessBase):
    id: int
    user_id: int
    stage: BusinessStageEnum
    logo_url: str | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': ESTABLISHED_BUSINESS_EXAMPLE},
    )
