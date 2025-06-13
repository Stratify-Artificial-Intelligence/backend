from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import UserRoleEnum


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(50))
    external_id = Column(String(50), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    role: Column[Enum] = Column(
        Enum(
            UserRoleEnum,
            values_callable=(lambda enum_class: [role.value for role in enum_class]),
        ),
        nullable=False,
    )
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=True)
    payment_service_user_id = Column(String(100), nullable=True)
    payment_service_subscription_id = Column(String(100), nullable=True)

    # Relationships
    businesses = relationship(
        'Business',
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    plan = relationship('Plan', back_populates='users', lazy='selectin')
