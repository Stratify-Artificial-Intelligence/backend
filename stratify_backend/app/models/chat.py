from sqlalchemy.orm import relationship

from app.database import Base

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String

from app.enums import ChatMessageSenderEnum


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    internal_id = Column(String, nullable=True, unique=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    messages = relationship(
        'ChatMessage',
        back_populates='chat',
        lazy='selectin',
        cascade='all, delete-orphan',
    )


class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=True, index=True)
    time = Column(DateTime(timezone=True), nullable=False)
    sender: Column[Enum] = Column(
        Enum(
            ChatMessageSenderEnum,
            values_callable=(lambda enum_class: [sender.value for sender in enum_class]),
        ),
    )
    content = Column(String, nullable=False, unique=True)

    # Relationships
    chat = relationship('Chat', back_populates='chat_messages')
