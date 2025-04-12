# noqa: D100
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domain import (
    Business as BusinessDomain,
    Chat as ChatDomain,
    ChatMessage as ChatMessageDomain,
)
from app.enums import BusinessStageEnum, ChatMessageSenderEnum
from app.repositories import ChatRepository, UserRepository, BusinessRepository
from app.services import openai
from app import deps


@pytest.fixture
def test_business() -> BusinessDomain:
    return BusinessDomain(
        id=1,
        user_id=1,
        stage=BusinessStageEnum.IDEA,
        name='Veyra',
        location='Spain',
        description='Veyra is super cool!',
        goal='Help entrepreneurs',
        team_size=3,
        team_description='Super nice guys.',
    )


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
def test_message_response() -> ChatMessageDomain:
    return ChatMessageDomain(
        id=2,
        chat_id=1,
        time=datetime.fromisoformat('2020-05-08T13:00:00+00:00'),
        sender=ChatMessageSenderEnum.AI_MODEL,
        content='This is a test response.',
    )


@pytest.fixture
def test_chat(test_message) -> ChatDomain:
    return ChatDomain(
        id=1,
        internal_id='id_test',
        title='Chat A',
        start_time=datetime.fromisoformat('2020-05-08T13:00:00+00:00'),
        business_id=1,
        messages=[test_message],
    )


@pytest.fixture
def test_chat_2() -> ChatDomain:
    return ChatDomain(
        id=2,
        internal_id='id_test_2',
        title='Chat B',
        start_time=datetime.fromisoformat('2020-05-08T13:00:00+00:00'),
        business_id=1,
        messages=[],
    )


@patch.object(ChatRepository, 'get_multi')
@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_list_chats(
    mock_get_user,
    mock_get_business,
    mock_get_multi,
    test_user,
    test_business,
    test_chat,
    test_chat_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get_business.return_value = test_business
    mock_get_multi.return_value = [test_chat, test_chat_2]

    expected_response = [
        {
            'id': 1,
            'title': 'Chat A',
            'start_time': '2020-05-08T13:00:00Z',
            'business_id': 1,
        },
        {
            'id': 2,
            'title': 'Chat B',
            'start_time': '2020-05-08T13:00:00Z',
            'business_id': 1,
        },
    ]
    actual_response = await async_client.get(
        '/businesses/1/chats',
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'get')
@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_get_chat_by_id(
    mock_get_user,
    mock_get_business,
    mock_get,
    test_user,
    test_business,
    test_chat,
    superuser_token_headers,
    async_client: AsyncClient,
):
    # ToDo (pduran): Add messages to the Chat.
    mock_get_user.return_value = test_user
    mock_get_business.return_value = test_business
    mock_get.return_value = test_chat

    expected_response = {
        'id': 1,
        'title': 'Chat A',
        'start_time': '2020-05-08T13:00:00Z',
        'business_id': 1,
        'messages': [
            {
                'id': 1,
                'time': '2020-05-08T13:00:00Z',
                'sender': 'user',
                'content': 'This is a test message.',
            }
        ],
    }
    actual_response = await async_client.get(
        '/businesses/1/chats/1',
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(ChatRepository, 'get')
@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_get_chat_by_id_not_found(
    mock_get_user,
    mock_get_business,
    mock_get,
    test_user,
    test_business,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get_business.return_value = test_business
    mock_get.return_value = None

    expected_response = {'detail': 'Chat not found'}
    actual_response = await async_client.get(
        '/businesses/1/chats/99',
        headers=superuser_token_headers,
    )

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


# ToDo (pduran): Solve the issue with the test.
@pytest.mark.skip(
    'Test not working as expected, since deps mock is not working as expected.'
)
@patch.object(deps, 'create_chat_in_service')
@patch.object(ChatRepository, 'create')
@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_create_chat(
    mock_get_user,
    mock_get_business,
    mock_create,
    mock_create_chat_openai,
    test_user,
    test_business,
    test_chat_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get_business.return_value = test_business
    mock_create.return_value = test_chat_2
    mock_create_chat_openai.return_value = 'id_test'

    expected_response = test_chat_2.model_dump()
    actual_response = await async_client.post(
        '/businesses/1/chats',
        json={},
        headers=superuser_token_headers,
    )

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


# ToDo (pduran): Solve the issue with the test.
@pytest.mark.skip(
    'Test not working as expected, since mocks are not working as expected.'
)
@patch.object(openai, 'add_message_to_chat_and_get_response')
@patch.object(ChatRepository, 'add_message')
@patch.object(ChatRepository, 'get')
@patch.object(BusinessRepository, 'get')
async def test_create_message(
    mock_get_chat,
    mock_get_business,
    mock_add_message,
    mock_add_message_openai,
    test_business,
    test_message,
    test_message_response,
    test_chat,
    async_client: AsyncClient,
):
    mock_get_business.return_value = test_business
    mock_add_message.return_value = [test_message, test_message_response]
    mock_get_chat.return_value = test_chat
    mock_add_message_openai.return_value = test_message_response.content

    expected_response = {
        'id': 1,
        'time': '2020-05-08T13:00:00Z',
        'sender': 'user',
        'content': 'This is a test message.',
    }
    message_data = {'content': 'This is a test message.'}
    actual_response = await async_client.post(
        '/businesses/1/chats/1/messages',
        json=message_data,
    )

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


# ToDo (pduran): Solve the issue with the test.
@pytest.mark.skip(
    'Test not working as expected, since mocks are not working as expected.'
)
@patch.object(ChatRepository, 'add_message')
@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_create_message_chat_not_found(
    mock_get_user,
    mock_get_business,
    mock_add_message,
    test_user,
    test_business,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get_business.return_value = test_business
    mock_add_message.return_value = None

    expected_response = {'detail': 'Chat not found'}
    message_data = {'content': 'This is a test message.'}
    actual_response = await async_client.post(
        '/businesses/1/chats/9/messages',
        json=message_data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_create_message_bad_request(
    mock_get_user,
    mock_get_business,
    test_user,
    test_business,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get_business.return_value = test_business

    expected_response = 'Field required'
    actual_response = await async_client.post(
        '/businesses/1/chats/1/messages', json={}, headers=superuser_token_headers
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']
