# noqa: D100
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domain import Chat as ChatDomain, ChatMessage as ChatMessageDomain
from app.enums import ChatMessageSenderEnum
from app.repositories import ChatRepository


@pytest.fixture
def test_message() -> ChatMessageDomain:
    return ChatMessageDomain(
        id=1,
        chat_id=1,
        time=datetime.fromisoformat('2020-05-08T13:00:00+00:00'),
        sender=ChatMessageSenderEnum.USER,
        content='This is a test message.',
    )


@pytest.fixture
def test_chat(test_message) -> ChatDomain:
    return ChatDomain(
        id=1,
        title='Chat A',
        start_time=datetime.fromisoformat('2020-05-08T13:00:00+00:00'),
        messages=[test_message],
    )


@pytest.fixture
def test_chat_2() -> ChatDomain:
    return ChatDomain(
        id=2,
        title='Chat B',
        start_time=datetime.fromisoformat('2020-05-08T13:00:00+00:00'),
        messages=[],
    )


@patch.object(ChatRepository, 'get_multi')
async def test_list_chats(
    mock_get_multi,
    test_chat,
    test_chat_2,
    async_client: AsyncClient,
):
    mock_get_multi.return_value = [test_chat, test_chat_2]

    expected_response = [
        {'id': 1, 'title': 'Chat A', 'start_time': '2020-05-08T13:00:00Z'},
        {'id': 2, 'title': 'Chat B', 'start_time': '2020-05-08T13:00:00Z'},
    ]
    actual_response = await async_client.get('/chats/')

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'get')
async def test_get_chat_by_id(mock_get, test_chat, async_client: AsyncClient):
    # ToDo (pduran): Add messages to the Chat.
    mock_get.return_value = test_chat

    expected_response = {
        'id': 1,
        'title': 'Chat A',
        'start_time': '2020-05-08T13:00:00Z',
        'messages': [
            {
                'id': 1,
                'time': '2020-05-08T13:00:00Z',
                'sender': 'user',
                'content': 'This is a test message.',
            }
        ],
    }
    actual_response = await async_client.get('/chats/1')

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'get')
async def test_get_chat_by_id_not_found(mock_get, async_client: AsyncClient):
    mock_get.return_value = None

    expected_response = {'detail': 'Chat not found'}
    actual_response = await async_client.get('/chats/99')

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'create')
async def test_create_chat(mock_create, test_chat_2, async_client: AsyncClient):
    mock_create.return_value = test_chat_2

    expected_response = {
        'id': 2,
        'title': 'Chat B',
        'start_time': '2020-05-08T13:00:00Z',
    }
    actual_response = await async_client.post('/chats/', json={})

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'add_message')
async def test_create_message(mock_add_message, test_message, async_client: AsyncClient):
    mock_add_message.return_value = test_message

    expected_response = {
        'id': 1,
        'time': '2020-05-08T13:00:00Z',
        'sender': 'user',
        'content': 'This is a test message.',
    }
    message_data = {'content': 'This is a test message.'}
    actual_response = await async_client.post('/chats/1/messages', json=message_data)

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'add_message')
async def test_create_message_chat_not_found(
    mock_add_message,
    async_client: AsyncClient,
):
    mock_add_message.return_value = None

    expected_response = {'detail': 'Chat not found'}
    message_data = {'content': 'This is a test message.'}
    actual_response = await async_client.post('/chats/9/messages', json=message_data)

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


async def test_create_message_bad_request(async_client: AsyncClient):
    expected_response = 'Field required'
    actual_response = await async_client.post('/chats/1/messages', json={})

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']
