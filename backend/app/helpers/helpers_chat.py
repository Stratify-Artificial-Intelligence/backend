from datetime import datetime

from app.domain import (
    Business as BusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    User as UserDomain,
)
from app.enums import ChatMessageSenderEnum, UserPlanEnum
from app.helpers.helpers_rag import get_context_for_business
from app.repositories import ChatRepository, PlanRepository
from app.services.openai import (
    add_message_to_chat,
    add_message_to_chat_and_get_response,
    create_chat,
)


async def add_store_message_and_get_store_response(
    chat: ChatDomain,
    message: ChatMessageDomain,
    user: UserDomain,
    chats_repo: ChatRepository,
    plans_repo: PlanRepository,
) -> ChatMessageDomain | None:
    """Register message and get the AI response."""
    await chats_repo.add_message(message)
    should_context_include_general_rag = await _should_chat_context_include_general_rag(
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


async def _should_chat_context_include_general_rag(
    user: UserDomain,
    plans_repo: PlanRepository,
) -> bool:
    """Determine if the general RAG should be included in chat context"""
    return (
        user.plan_id is not None
        and (plan := await plans_repo.get(plan_id=user.plan_id)) is not None
        and plan.name == UserPlanEnum.CEO
    )
