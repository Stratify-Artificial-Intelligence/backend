"""API endpoints for chat management."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import (
    user_can_create_chat,
    user_can_publish_message,
    user_can_read_chat,
)
from app.deps import get_business, get_current_active_user, get_repository
from app.domain import (
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
    User as UserDomain,
)
from app.enums import ChatMessageSenderEnum
from app.helpers import (
    add_message_to_external_chat,
    add_store_message_and_get_store_response,
    create_chat_in_service,
    get_chat_title,
)
from app.repositories import (
    ChatRepository,
    BusinessRepository,
    PlanRepository,
)
from app.schemas import Chat, ChatBase, ChatMessage, ChatMessageContent

router = APIRouter(
    tags=['Chat'],
    prefix='/businesses/{business_id}/chats',
)


@router.get(
    '',
    summary='List chats',
    response_model=list[ChatBase],
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def list_chats(
    business_id: int,
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """List all chats of a business."""
    await get_business(
        business_id=business_id,
        user=current_user,
        business_repo=business_repo,
        permission_func=user_can_read_chat,
    )
    return await chats_repo.get_multi(business_id=business_id)


@router.get(
    '/{chat_id}',
    summary='Get chat by ID',
    response_model=Chat,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def get_chat_by_id(
    business_id: int,
    chat_id: int,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    await get_business(
        business_id=business_id,
        user=current_user,
        business_repo=business_repo,
        permission_func=user_can_read_chat,
    )
    chat = await chats_repo.get(business_id=business_id, chat_id=chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Chat not found',
        )
    return chat


@router.post(
    '',
    summary='Create chat',
    response_model=ChatBase,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def create_chat(
    business_id: int,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    business = await get_business(
        business_id=business_id,
        user=current_user,
        business_repo=business_repo,
        permission_func=user_can_create_chat,
        load_hierarchy=True,
    )
    chat_title = await get_chat_title(business=business, chats_repo=chats_repo)
    chat_internal_id = await create_chat_in_service()
    chat = ChatDomain(
        internal_id=chat_internal_id,
        title=chat_title,
        start_time=datetime.now(),
        business_id=business_id,
    )
    # Initialize chat with context
    await add_message_to_external_chat(
        chat=chat,
        message_content=business.get_information(),
    )
    return await chats_repo.create(chat)


@router.post(
    '/{chat_id}/messages',
    summary='Add message to a chat',
    response_model=ChatMessage,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def add_message(
    business_id: int,
    chat_id: int,
    message_content: ChatMessageContent,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Add message to a chat with user as sender."""
    await get_business(
        business_id=business_id,
        user=current_user,
        business_repo=business_repo,
        permission_func=user_can_publish_message,
    )
    message = ChatMessageDomain(
        chat_id=chat_id,
        time=datetime.now(),
        sender=ChatMessageSenderEnum.USER,
        content=message_content.content,
    )
    chat = await chats_repo.get(business_id=business_id, chat_id=chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Chat not found',
        )
    response_message = await add_store_message_and_get_store_response(
        chat=chat,
        message=message,
        user=current_user,
        chats_repo=chats_repo,
        plans_repo=plans_repo,
    )
    if response_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Chat not found',
        )
    return response_message
