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
async def test_list_tests(mock_get_multi, async_client: AsyncClient):
    mock_get_multi.return_value = [
        TestDomain(id=1, name='Test A'),
        TestDomain(id=2, name='Test B', description='I am test B'),
    ]

    expected_response = [
        {'id': 1, 'name': 'Test A', 'description': None},
        {'id': 2, 'name': 'Test B', 'description': 'I am test B'},
    ]
    actual_response = await async_client.get('/tests')

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'get')
async def test_get_test_by_id(mock_get, async_client: AsyncClient):
    mock_get.return_value = TestDomain(id=1, name='Test A')

    expected_response = {'id': 1, 'name': 'Test A', 'description': None}
    actual_response = await async_client.get('/tests/1')

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'get')
async def test_get_test_by_id_not_found(mock_get, async_client: AsyncClient):
    mock_get.return_value = None

    expected_response = {'detail': 'Test not found'}
    actual_response = await async_client.get('/tests/99')

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'create')
async def test_create_test(mock_create, async_client: AsyncClient):
    mock_create.return_value = TestDomain(id=1, name='Test A')

    expected_response = {'id': 1, 'name': 'Test A', 'description': None}
    test_data = {'name': 'Test A'}
    actual_response = await async_client.post('/tests', json=test_data)

    assert status.HTTP_201_CREATED == actual_response.status_code
    assert expected_response == actual_response.json()


async def test_create_test_bad_request(async_client: AsyncClient):
    expected_response = 'Field required'
    test_data = {'description': 'I am test B'}
    actual_response = await async_client.post('/tests', json=test_data)

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']


@patch.object(TestRepository, 'update')
@patch.object(TestRepository, 'get')
async def test_update_test(mock_get, mock_update, async_client: AsyncClient):
    mock_get.return_value = TestDomain(id=1, name='Test A', description='I am test A')
    mock_update.return_value = TestDomain(id=1, name='Updated Test A', description=None)

    expected_response = {'id': 1, 'name': 'Updated Test A', 'description': None}
    test_data = {'name': 'Updated Test A'}
    actual_response = await async_client.put('/tests/1', json=test_data)

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'get')
async def test_update_test_not_found(mock_get, async_client: AsyncClient):
    mock_get.return_value = None

    expected_response = {'detail': 'Test not found'}
    test_data = {'name': 'Updated Test A'}
    actual_response = await async_client.put('/tests/99', json=test_data)

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'get')
async def test_update_test_bad_request(mock_get, async_client: AsyncClient):
    mock_get.return_value = TestDomain(id=1, name='Test A', description='I am test A')

    expected_response = 'Field required'
    test_data = {'description': 'I am test AAAA'}
    actual_response = await async_client.put('/tests/1', json=test_data)

    assert status.HTTP_422_UNPROCESSABLE_ENTITY == actual_response.status_code
    assert expected_response == actual_response.json()['detail'][0]['msg']


@patch.object(TestRepository, 'update')
@patch.object(TestRepository, 'get')
async def test_partial_update_test(mock_get, mock_update, async_client: AsyncClient):
    mock_get.return_value = TestDomain(id=1, name='Test A', description='I am test A')
    mock_update.return_value = TestDomain(
        id=1,
        name='Updated Test A',
        description='I am test A',
    )

    expected_response = {'id': 1, 'name': 'Updated Test A', 'description': 'I am test A'}
    test_data = {'name': 'Updated Test A'}
    actual_response = await async_client.patch('/tests/1', json=test_data)

    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'get')
async def test_partial_update_test_not_found(mock_get, async_client: AsyncClient):
    mock_get.return_value = None

    expected_response = {'detail': 'Test not found'}
    test_data = {'name': 'Updated Test A'}
    actual_response = await async_client.patch('/tests/99', json=test_data)

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()


@patch.object(TestRepository, 'delete')
@patch.object(TestRepository, 'get')
async def test_delete_test(mock_get, mock_delete, async_client: AsyncClient):
    mock_get.return_value = TestDomain(id=1, name='Test A')

    expected_content = b''
    actual_response = await async_client.delete('/tests/1')

    assert status.HTTP_204_NO_CONTENT == actual_response.status_code
    assert expected_content == actual_response.content


@patch.object(TestRepository, 'get')
async def test_delete_test_not_found(mock_get, async_client: AsyncClient):
    mock_get.return_value = None

    expected_response = {'detail': 'Test not found'}
    actual_response = await async_client.delete('/tests/99')

    assert status.HTTP_404_NOT_FOUND == actual_response.status_code
    assert expected_response == actual_response.json()
