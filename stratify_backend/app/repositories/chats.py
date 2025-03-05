from sqlalchemy.orm import selectinload

from app.models import Chat, ChatMessage
from app.domain import Chat as ChatDomain, ChatMessage as ChatMessageDomain
from app.repositories import BaseRepository

from sqlalchemy import select


class ChatRepository(BaseRepository):
    async def get(self, chat_id: int) -> ChatDomain | None:
        chat = await self._get(chat_id=chat_id, include_messages=True)
        if chat is None:
            return None
        return ChatDomain.model_validate(chat)

    async def get_multi(self) -> list[ChatDomain]:
        query = select(Chat)
        result = await self._db.execute(query)
        chats = result.scalars().all()
        return [ChatDomain.model_validate(chat) for chat in chats]

    async def create(self, chat_in: ChatDomain) -> ChatDomain:
        new_chat = Chat(title=chat_in.title, start_time=chat_in.start_time)
        self._db.add(new_chat)
        await self.commit()
        await self._db.refresh(new_chat)
        return ChatDomain.model_validate(new_chat)

    async def add_message(
        self,
        message: ChatMessageDomain,
    ) -> ChatMessageDomain | None:
        chat = await self._get(chat_id=message.chat_id, include_messages=False)
        if chat is None:
            return None
        new_message = ChatMessage(
            chat_id=message.chat_id,
            time=message.time,
            sender=message.sender,
            content=message.content,
        )
        chat.messages.append(new_message)
        await self.commit()
        return ChatMessageDomain.model_validate(new_message)

    async def _get(self, chat_id: int, include_messages: bool) -> Chat | None:
        query = select(Chat).where(Chat.id == chat_id)
        if include_messages:
            query = query.options(selectinload(Chat.messages))
        result = await self._db.execute(query)
        return result.scalars().one_or_none()
