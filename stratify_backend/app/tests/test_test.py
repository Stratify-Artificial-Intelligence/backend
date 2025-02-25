# noqa: D100
from fastapi import status


def test_placeholder():  # noqa: D103
    assert 1 == 1


async def test_tests_dummy(async_client):
    expected_response = {'test': 'test'}
    actual_response = await async_client.get('/tests/dummy')
    assert status.HTTP_200_OK == actual_response.status_code
    assert expected_response == actual_response.json()
