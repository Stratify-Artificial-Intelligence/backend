from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import ChatMessageSenderEnum


class ChatMessage(BaseModel):
    id: int | None = None
    chat_id: int
    time: datetime
    sender: ChatMessageSenderEnum
    content: str

    model_config = ConfigDict(from_attributes=True)


class Chat(BaseModel):
    id: int | None = None
    internal_id: str
    title: str
    start_time: datetime
    business_id: int
    messages: list[ChatMessage] | None = None

    model_config = ConfigDict(from_attributes=True)
