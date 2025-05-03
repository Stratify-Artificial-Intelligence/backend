"""API endpoints for business research management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import user_can_read_business
from app.deps import deep_research_for_business, get_current_active_user, get_repository
from app.domain import User as UserDomain
from app.repositories import BusinessRepository
from app.schemas import BusinessResearch, BusinessResearchParams

router = APIRouter(
    tags=['Business research'],
    prefix='/businesses/{business_id}/researches',
)


@router.post(
    '',
    summary='Create a research for a business',
    response_model=BusinessResearch,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def create_business_research(
    business_id: int,
    research_params: BusinessResearchParams,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Create a research for a business."""
    business = await business_repo.get_child(business_id=business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Business not found',
        )
    if not user_can_read_business(business, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not have enough privileges.',
        )
    return deep_research_for_business(business=business, params=research_params)
