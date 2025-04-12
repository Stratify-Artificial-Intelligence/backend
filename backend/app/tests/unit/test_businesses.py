# noqa: D100
from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.domain import (
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
)
from app.enums import BusinessStageEnum, CurrencyUnitEnum
from app.repositories import BusinessRepository, UserRepository


@pytest.fixture
def test_business_idea() -> BusinessIdeaDomain:
    return BusinessIdeaDomain(
        id=5,
        user_id=1,
        stage=BusinessStageEnum.IDEA,
        name='Veyra',
        location='Spain',
        description='Veyra is super cool!',
        goal='Help entrepreneurs',
        team_size=3,
        team_description='Super nice guys.',
        competitor_existence=True,
        competitor_differentiation='Well, we are the best.',
        investment=0,
        investment_currency=CurrencyUnitEnum.EURO,
    )


@pytest.fixture
def test_established_business() -> EstablishedBusinessDomain:
    return EstablishedBusinessDomain(
        id=6,
        user_id=1,
        stage=BusinessStageEnum.ESTABLISHED,
        name='Veyra',
        location='Spain',
        description='Veyra is super cool!',
        goal='Help entrepreneurs',
        team_size=3,
        team_description='Super nice guys.',
        billing=1000,
        billing_currency=CurrencyUnitEnum.EURO,
        ebitda=50,
        ebitda_currency=CurrencyUnitEnum.EURO,
        profit_margin=5,
    )



@patch.object(BusinessRepository, 'get_multi')
@patch.object(UserRepository, 'get_by_username')
async def test_list_businesses(
    mock_get_user,
    mock_get_multi,
    test_user,
    test_business_idea,
    test_established_business,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get_multi.return_value = [test_business_idea, test_established_business]

    expected_response = [
        test_business_idea.model_dump(),
        test_established_business.model_dump(),
    ]
    actual_response = await async_client.get(
        '/businesses',
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_get_business_by_id(
    mock_get_user,
    mock_get,
    test_user,
    test_business_idea,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get.return_value = test_business_idea

    expected_response = test_business_idea.model_dump()
    actual_response = await async_client.get(
        'businesses/5',
        headers=superuser_token_headers,
    )

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(BusinessRepository, 'get')
@patch.object(UserRepository, 'get_by_username')
async def test_get_business_by_id_not_found(
    mock_get_user,
    mock_get,
    test_user,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_get.return_value = None

    expected_response = {'detail': 'Business not found'}
    actual_response = await async_client.get(
        '/businesses/99',
        headers=superuser_token_headers,
    )

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(BusinessRepository, 'create_idea')
@patch.object(UserRepository, 'get_by_username')
async def test_create_business_idea(
    mock_get_user,
    mock_create,
    test_user,
    test_business_idea,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_create.return_value = test_business_idea

    data = test_business_idea.model_dump()
    del data['id'], data['user_id'], data['stage']
    expected_response = test_business_idea.model_dump()
    actual_response = await async_client.post(
        '/businesses/ideas',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'get_by_username')
async def test_create_business_idea_bad_request(
    mock_get_user,
    test_user,
    test_business_idea,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user

    data = test_business_idea.model_dump()
    del data['id'], data['user_id'], data['stage'], data['name']
    expected_response = 'Field required'
    actual_response = await async_client.post(
        '/businesses/ideas',
        json={},
        headers=superuser_token_headers,
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']


@patch.object(BusinessRepository, 'create_established')
@patch.object(UserRepository, 'get_by_username')
async def test_create_established_business(
    mock_get_user,
    mock_create,
    test_user,
    test_established_business,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user
    mock_create.return_value = test_established_business

    data = test_established_business.model_dump()
    del data['id'], data['user_id'], data['stage']
    expected_response = test_established_business.model_dump()
    actual_response = await async_client.post(
        '/businesses/established',
        json=data,
        headers=superuser_token_headers,
    )

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(UserRepository, 'get_by_username')
async def test_create_established_business_bad_request(
    mock_get_user,
    test_user,
    test_established_business,
    superuser_token_headers,
    async_client: AsyncClient,
):
    mock_get_user.return_value = test_user

    data = test_established_business.model_dump()
    del data['id'], data['user_id'], data['stage'], data['name']
    expected_response = 'Field required'
    actual_response = await async_client.post(
        '/businesses/established',
        json={},
        headers=superuser_token_headers,
    )

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']
