"""API endpoints for testing"""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
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


@router.get(
    '/{test_id}',
    summary='Get test by ID',
    response_model=Test,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def get_test_by_id(
    test_id: int,
    tests_repo: TestRepository = Depends(get_repository(TestRepository)),
):
    test = await tests_repo.get(test_id)
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Test not found',
        )
    return test


@router.post(
    '/',
    summary='Create test',
    response_model=Test,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
    },
)
async def create_test(
    test_data: TestCreate,
    tests_repo: TestRepository = Depends(get_repository(TestRepository)),
):
    test = TestDomain.model_validate(test_data)
    return await tests_repo.create(test)


@router.delete(
    '/{test_id}',
    summary='Delete test by ID',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def delete_test(
    test_id: int,
    tests_repo: TestRepository = Depends(get_repository(TestRepository)),
):
    test = await tests_repo.get(test_id)
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Test not found',
        )
    await tests_repo.delete(test)
    return None
