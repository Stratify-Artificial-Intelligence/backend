from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domain import User as UserDomain
from app.repositories import UserRepository


@pytest.fixture
def test_user() -> UserDomain:
    return UserDomain(
        id=1,
        username='User A',
        email='a@gmail.com',
        full_name='User A',
        is_active=True,
        password='test_password',
    )


@pytest.fixture
def test_user_2() -> UserDomain:
    return UserDomain(
        id=2,
        username='User B',
        email='b@gmail.com',
        full_name='User B',
        is_active=True,
        password='test_password_2',
    )


@patch.object(UserRepository, 'get_multi')
async def test_list_users(
    mock_get_multi,
    test_user,
    test_user_2,
    async_client: AsyncClient,
):
    mock_get_multi.return_value = [test_user, test_user_2]

    expected_response = [
        {
            'id': 1,
            'username': 'User A',
            'email': 'a@gmail.com',
            'full_name': 'User A',
            'is_active': True,
        },
        {
            'id': 2,
            'username': 'User B',
            'email': 'b@gmail.com',
            'full_name': 'User B',
            'is_active': True,
        },
    ]
    actual_response = await async_client.get('/users')

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'create')
@patch.object(UserRepository, 'get_by_username')
async def test_create_user(
    mock_get_by_username,
    mock_create,
    test_user,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = None
    mock_create.return_value = test_user

    expected_response = {
        'id': 1,
        'username': 'User A',
        'email': 'a@gmail.com',
        'full_name': 'User A',
        'is_active': True,
    }
    data = test_user.model_dump()
    del data['id']
    actual_response = await async_client.post('/users', json=data)

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'get_by_username')
async def test_create_user_already_exists(
    mock_get_by_username,
    test_user,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user

    expected_response = 'User already exists'
    data = test_user.model_dump()
    del data['id']
    response = await async_client.post('/users', json=data)

    assert status.HTTP_400_BAD_REQUEST == response.status_code
    assert expected_response == response.json()['detail']


async def test_create_user_bad_request(async_client: AsyncClient):
    expected_response = 'Field required'
    test_data = {'full_name': 'I am test B'}
    actual_response = await async_client.post('/users', json=test_data)

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']
