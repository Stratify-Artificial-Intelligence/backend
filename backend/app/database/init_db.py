import asyncio
from datetime import datetime, timedelta

from dateutil import tz

from app.database import async_session
from app.domain import (
    BusinessIdea as BusinessIdeaDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
    PlanBase as PlanBaseDomain,
    UserWithSecret as UserWithSecretDomain,
)
from app.enums import (
    BusinessStageEnum,
    ChatMessageSenderEnum,
    CurrencyUnitEnum,
    UserLanguageEnum,
    UserPlanEnum,
    UserRoleEnum,
)
from app.repositories import (
    BusinessRepository,
    ChatRepository,
    PlanRepository,
    UserRepository,
)

plans_data = [
    {
        'name': UserPlanEnum.STARTER.value,
        'is_active': True,
        'price': 0.0,
        'payment_service_price_id': 'price_1RVGgNIve8AXNk92PPGp2kvZ',
        'monthly_credits': 10,
    },
    {
        'name': UserPlanEnum.FOUNDER.value,
        'is_active': True,
        'price': 9.99,
        'payment_service_price_id': 'price_1RVGp2Ive8AXNk92AY707LgP',
        'monthly_credits': 25,
    },
]

users_data = [
    {
        'username': 'admin',
        'email': 'admin@gmail.com',
        'full_name': 'Admin user',
        'external_id': 'uEbFulRttShecs64P9s94am727A2',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
        'language': UserLanguageEnum.ES.value,
        'available_credits': None,
    },
    {
        'username': 'useruser',
        'email': 'user@gmail.com',
        'full_name': 'User user',
        'external_id': 'userexternalid',
        'is_active': True,
        'role': UserRoleEnum.BASIC.value,
        'language': UserLanguageEnum.ES.value,
        'plan_id': 1,
        'available_credits': 10,
    },
    {
        'username': 'service_user',
        'email': 'service_user@gmail.com',
        'full_name': 'Service user',
        'external_id': 'service_user',
        'is_active': True,
        'role': UserRoleEnum.SERVICE.value,
        'language': UserLanguageEnum.ES.value,
    },
]

businesses_idea_data = [
    {
        'user_id': 1,
        'stage': BusinessStageEnum.IDEA,
        'name': 'Veyra',
        'location': 'Spain',
        'description': 'Veyra is super cool!',
        'goal': 'Help entrepreneurs',
        'team_size': 3,
        'team_description': 'Super nice guys.',
        'user_position': 'CTO and backend developer',
        'extra_info': 'Here I could explain what the business is about',
        'competitor_existence': True,
        'competitor_differentiation': 'Well, we are the best.',
        'investment': 0,
        'investment_currency': CurrencyUnitEnum.EURO,
    }
]

established_businesses_data = [
    {
        'user_id': 1,
        'stage': BusinessStageEnum.ESTABLISHED,
        'name': 'Veyra',
        'location': 'Spain',
        'description': 'Veyra is super cool!',
        'goal': 'Help entrepreneurs',
        'team_size': 3,
        'team_description': 'Super nice guys.',
        'user_position': 'CTO and backend developer',
        'extra_info': 'Here I could explain what the business is about',
        'mission_and_vision': 'We try to be the best in class.',
        'billing': 1000,
        'billing_currency': CurrencyUnitEnum.EURO,
        'ebitda': 50,
        'ebitda_currency': CurrencyUnitEnum.EURO,
        'profit_margin': 5,
    }
]

chats_data = [
    {
        'title': 'Chat 1',
        'internal_id': 'internal_id1',
        'start_time': datetime.now(tz=tz.gettz('UTC')),
        'business_id': 1,
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
        'title': 'Chat 1',
        'internal_id': 'internal_id2',
        'start_time': datetime.now(tz=tz.gettz('UTC')),
        'business_id': 2,
    },
]


async def main() -> None:
    async with async_session() as session:
        plans_repo = PlanRepository(session)
        for plan_data in plans_data:
            plan = PlanBaseDomain.model_validate(plan_data)
            await plans_repo.create(plan)
        print('Initial plans data done')

        users_repo = UserRepository(session)
        for user_data in users_data:
            user = UserWithSecretDomain.model_validate(user_data)
            await users_repo.create(user)
        print('Initial users data done')

        businesses_repo = BusinessRepository(session)
        for business_idea_data in businesses_idea_data:
            business_idea = BusinessIdeaDomain.model_validate(business_idea_data)
            await businesses_repo.create_idea(business_idea)
        print('Businesses idea data done')

        for established_business_data in established_businesses_data:
            established_business = EstablishedBusinessDomain.model_validate(
                established_business_data,
            )
            await businesses_repo.create_established(established_business)
        print('Established businesses data done')

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
