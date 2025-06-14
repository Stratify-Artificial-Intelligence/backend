from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domain import User as UserDomain
from app.enums import UserRoleEnum
from app.repositories import UserRepository


@pytest.fixture
def test_user_2() -> UserDomain:
    return UserDomain(
        id=2,
        username='User B',
        email='b@gmail.com',
        full_name='User B',
        is_active=True,
        role=UserRoleEnum.ADMIN,
        plan_id=None,
    )


@pytest.fixture
def test_user_3() -> UserDomain:
    return UserDomain(
        id=3,
        username='User C',
        email='c@gmail.com',
        full_name='User C',
        is_active=True,
        role=UserRoleEnum.BASIC,
        plan_id=1,
    )


@patch.object(UserRepository, 'create')
async def test_signup_user(
    mock_create,
    test_user_3,
    async_client: AsyncClient,
):
    mock_create.return_value = test_user_3

    expected_response = {
        'id': 3,
        'username': 'User C',
        'email': 'c@gmail.com',
        'full_name': 'User C',
        'is_active': True,
        'role': UserRoleEnum.BASIC.value,
        'plan_id': 1,
    }
    data = test_user_3.model_dump()
    del data['id']
    del data['role']
    del data['is_active']
    del data['plan_id']
    del data['payment_service_user_id']
    del data['payment_service_subscription_id']
    data['external_id'] = 'test_external_id_3'
    actual_response = await async_client.post(
        '/users/signup',
        json=data,
    )
    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'create')
async def test_signup_user_already_exists(
    mock_create,
    test_user_3,
    async_client: AsyncClient,
):
    mock_create.side_effect = ValueError('Username already exists')

    expected_response = {'detail': 'Username already exists'}
    data = test_user_3.model_dump()
    del data['id']
    del data['role']
    del data['is_active']
    del data['plan_id']
    del data['payment_service_user_id']
    del data['payment_service_subscription_id']
    data['external_id'] = 'test_external_id_3'
    response = await async_client.post(
        '/users/signup',
        json=data,
    )

    assert status.HTTP_400_BAD_REQUEST == response.status_code
    assert expected_response == response.json()


async def test_signup_user_bad_request(
    test_user,
    async_client: AsyncClient,
):
    expected_response = 'Field required'
    test_data = {'full_name': 'I am test B'}
    actual_response = await async_client.post(
        '/users/signup',
        json=test_data,
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']


@patch.object(UserRepository, 'get_by_username')
async def test_read_users_me(
    mock_get_by_username,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user

    expected_response = {
        'id': 1,
        'username': 'User A',
        'email': 'a@gmail.com',
        'full_name': 'User A',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
        'plan_id': None,
    }
    actual_response = await async_client.get(
        '/users/me',
        headers=superuser_token_headers,
    )
    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'update')
@patch.object(UserRepository, 'get_by_username')
async def test_update_users_me(
    mock_get_by_username,
    mock_update,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    updated_user = test_user.model_copy()
    updated_user.full_name = 'User A with new name'
    mock_update.return_value = updated_user

    expected_response = {
        'id': 1,
        'username': 'User A',
        'email': 'a@gmail.com',
        'full_name': 'User A with new name',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
        'plan_id': None,
    }
    data = {
        'full_name': 'User A with nem name',
    }
    actual_response = await async_client.patch(
        '/users/me',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'update')
@patch.object(UserRepository, 'get_by_username')
async def test_update_users_me_already_exists(
    mock_get_by_username,
    mock_update,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_update.side_effect = ValueError('Username already exists')

    expected_response = {'detail': 'Username already exists'}
    data = {
        'username': 'User B',
    }
    response = await async_client.patch(
        '/users/me',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_400_BAD_REQUEST == response.status_code
    assert expected_response == response.json()


@patch.object(UserRepository, 'get_by_username')
async def test_update_users_me_bad_request(
    mock_get_by_username,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user

    expected_response = 'Extra inputs are not permitted'
    test_data = test_user.model_dump()
    actual_response = await async_client.patch(
        '/users/me',
        json=test_data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']


@patch.object(UserRepository, 'get_multi')
@patch.object(UserRepository, 'get_by_username')
async def test_list_users(
    mock_get_by_username,
    mock_get_multi,
    test_user,
    test_user_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_get_multi.return_value = [test_user, test_user_2]

    expected_response = [
        {
            'id': 1,
            'username': 'User A',
            'email': 'a@gmail.com',
            'full_name': 'User A',
            'is_active': True,
            'role': UserRoleEnum.ADMIN.value,
            'plan_id': None,
        },
        {
            'id': 2,
            'username': 'User B',
            'email': 'b@gmail.com',
            'full_name': 'User B',
            'is_active': True,
            'role': UserRoleEnum.ADMIN.value,
            'plan_id': None,
        },
    ]
    actual_response = await async_client.get(
        '/users',
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_read_user_by_id(
    mock_get_by_username,
    mock_get,
    test_user,
    test_user_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_get.return_value = test_user_2

    expected_response = {
        'id': 2,
        'username': 'User B',
        'email': 'b@gmail.com',
        'full_name': 'User B',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
        'plan_id': None,
    }
    actual_response = await async_client.get(
        '/users/2',
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_read_user_by_id_not_found(
    mock_get_by_username,
    mock_get,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_get.return_value = None

    expected_response = {'detail': 'User not found'}
    actual_response = await async_client.get(
        '/users/99',
        headers=superuser_token_headers,
    )

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'create')
@patch.object(UserRepository, 'get_by_username')
async def test_create_user(
    mock_get_by_username,
    mock_create,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_create.return_value = test_user

    expected_response = {
        'id': 1,
        'username': 'User A',
        'email': 'a@gmail.com',
        'full_name': 'User A',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
        'plan_id': None,
    }
    data = test_user.model_dump()
    del data['id']
    del data['payment_service_user_id']
    del data['payment_service_subscription_id']
    data['external_id'] = 'test_external_id_3'
    actual_response = await async_client.post(
        '/users',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'create')
@patch.object(UserRepository, 'get_by_username')
async def test_create_user_already_exists(
    mock_get_by_username,
    mock_create,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_create.side_effect = ValueError('Username already exists')

    expected_response = 'Username already exists'
    data = test_user.model_dump()
    del data['id']
    del data['payment_service_user_id']
    del data['payment_service_subscription_id']
    data['external_id'] = 'test_external_id_3'
    response = await async_client.post(
        '/users',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_400_BAD_REQUEST == response.status_code
    assert expected_response == response.json()['detail']


@patch.object(UserRepository, 'get_by_username')
async def test_create_user_bad_request(
    mock_get_by_username,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user

    expected_response = 'Field required'
    test_data = {'full_name': 'I am test B'}
    actual_response = await async_client.post(
        '/users',
        json=test_data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']


@patch.object(UserRepository, 'update')
@patch.object(UserRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_update_user(
    mock_get_by_username,
    mock_get,
    mock_update,
    test_user,
    test_user_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_get.return_value = test_user_2
    updated_user = test_user_2.model_copy()
    updated_user.full_name = 'User B with new name'
    mock_update.return_value = updated_user

    expected_response = {
        'id': 2,
        'username': 'User B',
        'email': 'b@gmail.com',
        'full_name': 'User B with new name',
        'is_active': True,
        'role': UserRoleEnum.ADMIN.value,
        'plan_id': None,
    }
    data = {
        'full_name': 'User B with nem name',
    }
    actual_response = await async_client.patch(
        '/users/2',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'update')
@patch.object(UserRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_update_user_already_exists(
    mock_get_by_username,
    mock_get,
    mock_update,
    test_user,
    test_user_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user
    mock_get.return_value = test_user_2
    mock_update.side_effect = ValueError('Username already exists')

    expected_response = {'detail': 'Username already exists'}
    data = {
        'username': 'User A',
    }
    response = await async_client.patch(
        '/users/2',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_400_BAD_REQUEST == response.status_code
    assert expected_response == response.json()


@patch.object(UserRepository, 'get_by_username')
async def test_update_user_bad_request(
    mock_get_by_username,
    test_user,
    test_user_2,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_by_username.return_value = test_user

    expected_response = 'Extra inputs are not permitted'
    test_data = test_user_2.model_dump()
    actual_response = await async_client.patch(
        '/users/2',
        json=test_data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']
