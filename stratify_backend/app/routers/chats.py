"""API endpoints for chat management."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.deps import (
    add_store_message_and_get_store_response,
    create_chat_in_service,
    get_repository,
)
from app.domain import Chat as ChatDomain, ChatMessage as ChatMessageDomain
from app.enums import ChatMessageSenderEnum
from app.repositories import ChatRepository
from app.schemas import Chat, ChatBase, ChatMessageContent
from app.schemas.chat import ChatMessage

router = APIRouter(
    tags=['Chat'],
    prefix='/chats',
)


@router.get(
    '',
    summary='List chats',
    response_model=list[ChatBase],
)
async def list_chats(
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
):
    """List of all chats present in the database."""
    return await chats_repo.get_multi()


@router.get(
    '/{chat_id}',
    summary='Get chat by ID',
    response_model=Chat,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def get_chat_by_id(
    chat_id: int,
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
):
    chat = await chats_repo.get(chat_id)
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Chat not found',
        )
    return chat


@router.post(
    '/',
    summary='Create chat',
    response_model=ChatBase,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
    },
)
async def create_chat(
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
):
    chat_internal_id = await create_chat_in_service()
    chat = ChatDomain(
        internal_id=chat_internal_id,
        title='Chat title',
        start_time=datetime.now(),
    )
    return await chats_repo.create(chat)


@router.post(
    '/{chat_id}/messages',
    summary='Add message to a chat',
    response_model=ChatMessage,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def add_message(
    chat_id: int,
    message_content: ChatMessageContent,
    chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
):
    """Add message to a chat with user as sender."""
    message = ChatMessageDomain(
        chat_id=chat_id,
        time=datetime.now(),
        sender=ChatMessageSenderEnum.USER,
        content=message_content.content,
    )
    response_message = await add_store_message_and_get_store_response(
        message=message,
        chats_repo=chats_repo,
    )
    if response_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Chat not found',
        )
    return response_message
