from sqlalchemy.orm import relationship

from app.database import Base

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String

from app.enums import BusinessStageEnum, CurrencyUnitEnum


class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    goal = Column(String, nullable=True)
    stage: Column[Enum] = Column(
        Enum(
            BusinessStageEnum,
            values_callable=(lambda enum_class: [stage.value for stage in enum_class]),
        ),
    )
    team_size = Column(Integer, nullable=True)
    team_description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'business',
        'polymorphic_on': stage,
    }

    # Relationships
    user = relationship('User', back_populates='businesses', lazy='selectin')


class BusinessIdea(Business):
    __tablename__ = 'business_ideas'

    id = Column(Integer, ForeignKey('businesses.id'), primary_key=True)
    competitor_existence = Column(Boolean, nullable=True)
    competitor_differentiation = Column(String, nullable=True)
    investment = Column(Float, nullable=True)
    investment_currency: Column[Enum] = Column(
        Enum(
            CurrencyUnitEnum,
            values_callable=(
                lambda enum_class: [currency.value for currency in enum_class]
            ),
        ),
    )

    __mapper_args__ = {
        'polymorphic_identity': BusinessStageEnum.IDEA,
    }


class EstablishedBusiness(Business):
    __tablename__ = 'established_businesses'

    id = Column(Integer, ForeignKey('businesses.id'), primary_key=True)
    billing = Column(Float, nullable=True)
    billing_currency: Column[Enum] = Column(
        Enum(
            CurrencyUnitEnum,
            values_callable=(
                lambda enum_class: [currency.value for currency in enum_class]
            ),
        ),
    )
    ebitda = Column(Float, nullable=True)
    ebitda_currency: Column[Enum] = Column(
        Enum(
            CurrencyUnitEnum,
            values_callable=(
                lambda enum_class: [currency.value for currency in enum_class]
            ),
        ),
    )
    profit_margin = Column(Float, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': BusinessStageEnum.ESTABLISHED,
    }
