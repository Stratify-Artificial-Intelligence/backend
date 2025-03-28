from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.enums import UserRoleEnum


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50))
    full_name = Column(String(50))
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    role: Column[Enum] = Column(
        Enum(
            UserRoleEnum,
            values_callable=(lambda enum_class: [role.value for role in enum_class]),
        ),
        nullable=False,
    )

    # Relationships
    chats = relationship(
        'Chat',
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
