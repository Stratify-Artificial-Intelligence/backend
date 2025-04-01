import asyncio
from datetime import datetime, timedelta

from dateutil import tz

from app.database import async_session
from app.domain import (
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    UserWithSecret as UserWithSecretDomain,
)
from app.enums import ChatMessageSenderEnum, UserRoleEnum
from app.repositories import ChatRepository, UserRepository


users_data = [
    {
        'username': 'admin',
        'email': 'admin@gmail.com',
        'full_name': 'Admin user',
        'password': 'testtesttest',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
    },
    {
        'username': 'useruser',
        'email': 'user@gmail.com',
        'full_name': 'User user',
        'password': 'userpassword',
        'is_active': True,
        'role': UserRoleEnum.BASIC.value,
    },
]

chats_data = [
    {
        'title': 'chat1',
        'internal_id': 'internal_id1',
        'start_time': datetime.now(tz=tz.gettz('UTC')),
        'user_id': 1,
        'messages': [
            {
                'time': datetime.now(tz=tz.gettz('UTC')),
                'sender': ChatMessageSenderEnum.USER.value,
                'content': 'Hello',
            },
            {
                'time': datetime.now(tz=tz.gettz('UTC')) + timedelta(seconds=2),
                'sender': ChatMessageSenderEnum.AI_MODEL.value,
                'content': 'Hi',
            },
        ],
    },
    {
        'title': 'chat2',
        'internal_id': 'internal_id2',
        'start_time': datetime.now(tz=tz.gettz('UTC')),
        'user_id': 2,
    },
]


async def main() -> None:
    async with async_session() as session:
        users_repo = UserRepository(session)
        for user_data in users_data:
            user = UserWithSecretDomain.model_validate(user_data)
            await users_repo.create(user)
        print('Initial users data done')

        chats_repo = ChatRepository(session)
        for chat_data in chats_data:
            messages_data = chat_data.pop('messages', [])
            assert isinstance(messages_data, list)
            chat = ChatDomain.model_validate(chat_data)
            chat = await chats_repo.create(chat)
            messages = [
                ChatMessageDomain.model_validate(
                    {**message_data, 'chat_id': chat.id},
                )
                for message_data in messages_data
            ]
            for message in messages:
                await chats_repo.add_message(message)
        print('Initial chats and messages data done')
        await session.commit()
        await session.close()


if __name__ == '__main__':
    asyncio.run(main())
