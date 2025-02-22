"""API endpoints for testing"""

from fastapi import APIRouter, Depends

from app.deps import get_repository
from app.domain import Test as TestDomain
from app.repositories import TestRepository
from app.schemas.test import Test, TestCreate

router = APIRouter(
    tags=['Test'],
    prefix='/tests',
)


@router.get(
    '/dummy',
    summary='Dummy endpoint for testing.',
)
async def get_tests_dummy():
    """Dummy endpoint that always returns the same, just for testing. It does not
    interact with the database.
    """
    return {'test': 'test'}


@router.get(
    '/',
    summary='List tests',
    response_model=list[Test],
)
async def list_tests(
    tests_repo: TestRepository = Depends(get_repository(TestRepository)),
):
    """List of all tests present in the database."""
    return await tests_repo.get_multi()


@router.post(
    '/',
    response_model=Test,
    status_code=201,
)
async def create_test(
    test_data: TestCreate,
    tests_repo: TestRepository = Depends(get_repository(TestRepository)),
):
    test = TestDomain.model_validate(test_data)
    return await tests_repo.create(test)
