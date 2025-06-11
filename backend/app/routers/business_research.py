"""API endpoints for business research management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker, user_can_read_business
from app.deps import get_current_active_user, get_repository
from app.domain import User as UserDomain
from app.enums import UserRoleEnum
from app.helpers import (
    chunk_and_upload_text_for_business,
    chunk_and_upload_text_for_general,
    deep_research_for_business,
)
from app.repositories import BusinessRepository
from app.schemas import (
    BusinessResearch,
    BusinessResearchParams,
    GeneralResearch,
    GeneralResearchParams,
)
from app.settings import RAGSettings

rag_settings = RAGSettings()

router = APIRouter(
    tags=['Research'],
    prefix='/researches',
)


@router.post(
    '/general',
    summary='Create a general research',
    response_model=GeneralResearch,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def create_general_research(
    research_params: GeneralResearchParams,
):
    """Create a general research."""
    business_research = GeneralResearch(research=research_params.research)
    if research_params.store_result:
        chunk_and_upload_text_for_general(text=business_research.research)
    return business_research


@router.post(
    '/businesses/{business_id}',
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
    business_research = deep_research_for_business(
        business=business,
        params=research_params,
    )

    if research_params.store_result:
        chunk_and_upload_text_for_business(
            text=business_research.research,
            business_id=business_id,
        )

    return business_research
