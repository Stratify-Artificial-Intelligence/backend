from app.enums import ChatMessageSenderEnum, BusinessStageEnum, CurrencyUnitEnum

from pydantic import BaseModel, ConfigDict

from datetime import datetime


BUSINESS_BASE_EXAMPLE = {
    'name': 'Veyra',
    'location': 'Spain',
    'description': 'Veyra is super cool!',
    'goal': 'Help entrepreneurs',
    'team_size': 3,
    'team_description': 'Super nice guys.',
}

BUSINESS_EXAMPLE = {
    'id': 4,
    'user_id': 1,
    'stage': BusinessStageEnum.IDEA,
    **BUSINESS_BASE_EXAMPLE,
}

BUSINESS_IDEA_BASE_EXAMPLE = {
    **BUSINESS_BASE_EXAMPLE,
    'competitor_existance': True,
    'competitor_differentiation': 'Well, we are the best.',
    'investment': 0,
    'investment_currency': CurrencyUnitEnum.EURO,
}

BUSINESS_IDEA_EXAMPLE = {
    'id': 5,
    'user_id': 1,
    'stage': BusinessStageEnum.IDEA,
    **BUSINESS_IDEA_BASE_EXAMPLE,
}

ESTABLISHED_BUSINESS_BASE_EXAMPLE = {
    **BUSINESS_BASE_EXAMPLE,
    'billing': 1000,
    'billing_currency': CurrencyUnitEnum.EURO,
    'ebitda': 50,
    'ebitda_currency': CurrencyUnitEnum.EURO,
    'profit_margin': 5,
}

ESTABLISHED_BUSINESS_EXAMPLE = {
    'id': 6,
    'user_id': 1,
    'stage': BusinessStageEnum.ESTABLISHED,
    **ESTABLISHED_BUSINESS_BASE_EXAMPLE,
}


class BusinessBase(BaseModel):
    name: str
    location: str
    description: str | None = None
    goal: str | None = None
    team_size: int | None = None
    team_description: str | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_BASE_EXAMPLE},
    )


class Business(BusinessBase):
    id: int
    user_id: int
    stage: BusinessStageEnum

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_EXAMPLE},
    )


class BusinessIdeaBase(BusinessBase):
    competitor_existence: bool | None = None
    competitor_differentiation: str | None = None
    investment: float | None = None
    investment_currency: CurrencyUnitEnum | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_IDEA_BASE_EXAMPLE},
    )


class BusinessIdea(BusinessIdeaBase):
    id: int
    user_id: int
    stage: BusinessStageEnum

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': BUSINESS_IDEA_EXAMPLE},
    )


class EstablishedBusinessBase(BusinessBase):
    billing: float | None = None
    billing_currency: CurrencyUnitEnum | None = None
    ebitda: float | None = None
    ebitda_currency: CurrencyUnitEnum | None = None
    profit_margin: float | None = None

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': ESTABLISHED_BUSINESS_BASE_EXAMPLE},
    )


class EstablishedBusiness(EstablishedBusinessBase):
    id: int
    user_id: int
    stage: BusinessStageEnum

    model_config = ConfigDict(
        extra='forbid',
        json_schema_extra={'example': ESTABLISHED_BUSINESS_EXAMPLE},
    )
