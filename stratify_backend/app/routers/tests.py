"""API endpoints for testing"""
from typing import List

from fastapi import APIRouter

from app.schemas.test import Test

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
    response_model=List[Test],
)
async def list_tests():
    """List of all tests present in the database."""


