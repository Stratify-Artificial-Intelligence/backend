from datetime import datetime
from typing import Callable, Type

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_session
from app.domain import (
    Business as BusinessDomain,
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    User as UserDomain,
)
from app.enums import ChatMessageSenderEnum, UserPlanEnum
from app.helpers import get_context_for_business
from app.repositories import (
    BaseRepository,
    BusinessRepository,
    ChatRepository,
    PlanRepository,
    UserRepository,
)
from app.schemas import TokenData
from app.security import check_auth_token
from app.services.openai import (
    add_message_to_chat,
    add_message_to_chat_and_get_response,
    create_chat,
)


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def _get_repo(db: AsyncSession = Depends(get_session)) -> BaseRepository:
        return repo_type(db)

    return _get_repo


async def get_current_user(
    token_data: TokenData = Depends(check_auth_token),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserDomain:
    user = await users_repo.get_by_username(username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        )
    return user


async def get_current_active_user(
    current_user: UserDomain = Depends(get_current_user),
) -> UserDomain:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return current_user


async def get_business(
    business_id: int,
    user: UserDomain,
    business_repo: BusinessRepository,
    permission_func: Callable[[BusinessDomain, UserDomain], bool],
    load_hierarchy: bool = False,
) -> BusinessDomain | BusinessIdeaDomain | EstablishedBusinessDomain:
    business = (
        await business_repo.get_child(business_id=business_id)
        if load_hierarchy
        else await business_repo.get(business_id=business_id)
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Business not found',
        )
    if not permission_func(business, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not have enough privileges.',
        )
    return business


# ToDo (pduran): Should this function be here?
async def add_store_message_and_get_store_response(
    chat: ChatDomain,
    message: ChatMessageDomain,
    user: UserDomain,
    chats_repo: ChatRepository,
    plans_repo: PlanRepository,
) -> ChatMessageDomain | None:
    """Register message and get the AI response."""
    await chats_repo.add_message(message)
    should_context_include_general_rag = await should_chat_context_include_general_rag(
        user=user,
        plans_repo=plans_repo,
    )
    context = get_context_for_business(
        business_id=chat.business_id,
        query=message.content,
        should_include_general_rag=should_context_include_general_rag,
    )
    response_content = await add_message_to_chat_and_get_response(
        chat_internal_id=chat.internal_id,
        content=message.content,
        context=context,
    )
    # ToDo (pduran): Parallelize these two operations
    # _, response_content = await asyncio.gather(
    #     chats_repo.add_message(message),
    #     add_message_to_chat_and_get_response(
    #         chat_internal_id=chat.internal_id,
    #         content=message.content,
    #     ),
    # )
    response_message = ChatMessageDomain(
        chat_id=message.chat_id,
        time=datetime.now(),
        sender=ChatMessageSenderEnum.AI_MODEL,
        content=response_content,
    )
    return await chats_repo.add_message(response_message)


async def add_message_to_external_chat(
    chat: ChatDomain,
    message_content: str,
) -> None:
    """Add a message to an external chat."""
    add_message_to_chat(
        chat_internal_id=chat.internal_id,
        content=message_content,
    )


async def create_chat_in_service() -> str:
    """Create a chat in the external service and return its internal ID."""
    chat_internal_id = await create_chat()
    return chat_internal_id


async def get_chat_title(business: BusinessDomain, chats_repo: ChatRepository) -> str:
    """Get the chat title based on the business."""
    business_chats = await chats_repo.get_multi(business_id=business.id)
    num_chat = len(business_chats) + 1
    return f'Chat {num_chat}'


async def should_chat_context_include_general_rag(
    user: UserDomain,
    plans_repo: PlanRepository,
) -> bool:
    """Determine if the general RAG should be included in chat context"""
    return (
        user.plan_id is not None
        and (plan := await plans_repo.get(plan_id=user.plan_id)) is not None
        and plan.name == UserPlanEnum.CEO
    )
