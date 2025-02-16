"""API endpoints for testing"""

from fastapi import APIRouter


router = APIRouter(
    tags=['Test'],
    prefix='/test',
)


@router.get('/')
async def get_test():
    """Get test"""
    return {'test': 'test'}
