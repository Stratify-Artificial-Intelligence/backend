from app.enums import ChatMessageSenderEnum

from pydantic import BaseModel, ConfigDict

from datetime import datetime


class ChatMessageContent(BaseModel):
    content: str

    model_config = ConfigDict(extra='forbid')


class ChatMessage(ChatMessageContent):
    id: int
    time: datetime
    sender: ChatMessageSenderEnum


class ChatBase(BaseModel):
    id: int
    title: str
    start_date: datetime


class Chat(ChatBase):
    messages: list[ChatMessage]
