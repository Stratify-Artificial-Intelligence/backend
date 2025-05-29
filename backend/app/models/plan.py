from app.database import Base
from app.enums import UserPlanEnum

from sqlalchemy import Boolean, Column, Enum, Float, Integer
from sqlalchemy.orm import relationship


class Plan(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True)
    name: Column[Enum] = Column(
        Enum(
            UserPlanEnum,
            values_callable=(lambda enum_class: [plan.value for plan in enum_class]),
        ),
        nullable=False,
        unique=True,
    )
    is_active = Column(Boolean, nullable=False, default=True)
    price = Column(Float, nullable=False, default=0)

    # Relationships
    users = relationship(
        'User',
        back_populates='plan',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
