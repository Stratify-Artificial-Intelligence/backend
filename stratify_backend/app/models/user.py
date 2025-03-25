from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50))
    full_name = Column(String(50))
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    chats = relationship(
        'Chat',
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
