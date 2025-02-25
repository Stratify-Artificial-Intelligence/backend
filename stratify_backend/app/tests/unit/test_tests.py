# noqa: D100
from unittest.mock import patch

from fastapi import status
from httpx import AsyncClient

from app.domain import Test as TestDomain
from app.repositories import TestRepository


def test_placeholder():  # noqa: D103
    assert 1 == 1


async def test_tests_dummy(async_client):
    expected_response = {'test': 'test'}
    actual_response = await async_client.get('/tests/dummy')
    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'get_multi')
async def test_list_tests(
    mock_get_multi,
    async_client: AsyncClient,
):
    mock_get_multi.return_value = [
        TestDomain(id=1, name='Test A'),
        TestDomain(id=2, name='Test B', description='I am test B'),
    ]

    expected_response = [
        {'id': 1, 'name': 'Test A', 'description': None},
        {'id': 2, 'name': 'Test B', 'description': 'I am test B'},
    ]

    actual_response = await async_client.get('/tests/')

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()
