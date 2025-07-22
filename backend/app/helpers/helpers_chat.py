from datetime import datetime
from typing import AsyncGenerator

from fastapi import HTTPException, status

from app.domain import (
    Business as BusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    User as UserDomain,
)
from app.enums import ChatMessageSenderEnum, UserPlanEnum, UserRoleEnum
from app.helpers.helpers_rag import get_business_rag, get_general_rag
from app.repositories import ChatRepository, PlanRepository, UserRepository
from app.services import ServicesFactory


chat_ai_model_service = ServicesFactory().get_chat_ai_model_provider()


async def add_store_message_and_get_store_response(
    business: BusinessDomain,
    chat: ChatDomain,
    message: ChatMessageDomain,
    user: UserDomain,
    chats_repo: ChatRepository,
    plans_repo: PlanRepository,
) -> ChatMessageDomain | None:
    """Register message and get the AI response."""
    business_rag = get_business_rag(business_id=chat.business_id, query=message.content)
    should_context_include_general_rag = await _should_chat_context_include_general_rag(
        user=user,
        plans_repo=plans_repo,
    )
    general_rag = (
        get_general_rag(query=message.content)
        if should_context_include_general_rag
        else ''
    )
    response_content = await chat_ai_model_service.add_message_to_chat_and_get_response(
        business=business,
        chat=chat,
        content=message.content,
        business_rag=business_rag,
        general_rag=general_rag,
    )
    # Note: By storing the message after the AI response, we ensure that the message
    # is only saved after the response is successfully generated.
    await chats_repo.add_message(message)
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


async def add_store_message_and_get_store_response_stream(
    business: BusinessDomain,
    chat: ChatDomain,
    message: ChatMessageDomain,
    user: UserDomain,
    chats_repo: ChatRepository,
    plans_repo: PlanRepository,
) -> AsyncGenerator[str, None]:
    await chats_repo.add_message(message)

    business_rag = get_business_rag(business_id=chat.business_id, query=message.content)
    should_include_general_rag = await _should_chat_context_include_general_rag(
        user=user, plans_repo=plans_repo,
    )
    general_rag = (
        get_general_rag(query=message.content)
        if should_include_general_rag
        else ''
    )
    stream_gen = await chat_ai_model_service.add_message_to_chat_and_get_response_stream(
        business=business,
        chat=chat,
        content=message.content,
        business_rag=business_rag,
        general_rag=general_rag,
    )

    full_response = ''
    async for chunk in stream_gen:
        full_response += chunk
        yield chunk

    response_message = ChatMessageDomain(
        chat_id=message.chat_id,
        time=datetime.now(),
        sender=ChatMessageSenderEnum.AI_MODEL,
        content=full_response,
    )
    await chats_repo.add_message(response_message)


async def create_chat_in_service() -> str:
    """Create a chat in the external service and return its internal ID."""
    chat_internal_id = await chat_ai_model_service.create_chat()
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
    return user.role == UserRoleEnum.ADMIN or (
        user.plan_id is not None
        and (plan := await plans_repo.get(plan_id=user.plan_id)) is not None
        and plan.name == UserPlanEnum.CEO
    )


async def subtract_user_credits_for_new_message_in_chat(
    user: UserDomain,
    chat: ChatDomain,
    users_repo: UserRepository,
) -> None:
    """Subtract credits from user for sending a new message in a chat.

    Note:
    - If the user has `None` credits, no credits will be subtracted nor exception raised.

    Raises
    ------
    HTTPException
        If the user has not enough credits to cover sending the message.
    """
    if user.available_credits is None:
        return

    message_credit_cost = chat_ai_model_service.get_new_message_credit_cost(chat=chat)
    if user.available_credits < message_credit_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f'User {user.id} does not have enough credits to send a message in chat '
                f'{chat.id}. User has {user.available_credits} credits, but the message '
                f'costs {message_credit_cost} credits.'
            ),
        )

    user.available_credits -= message_credit_cost
    await users_repo.update(user_id=user.id, user_update=user)
