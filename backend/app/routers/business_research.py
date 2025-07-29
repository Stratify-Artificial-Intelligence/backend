"""API endpoints for business research management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker, user_can_read_business
from app.deps import get_current_active_user, get_repository
from app.domain import User as UserDomain
from app.enums import ResearchRequestStatusEnum, UserRoleEnum
from app.helpers import (
    chunk_and_upload_text,
    deep_research_for_business,
    deep_research_for_business_async,
)
from app.helpers.helpers_rag import get_deep_research_async
from app.repositories import BusinessRepository
from app.schemas import Research, ResearchExtended, ResearchParams, ResearchStoreParams


router = APIRouter(
    tags=['Research'],
    prefix='/researches',
)


@router.post(
    '',
    summary='Create a research',
    response_model=ResearchExtended,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def create_research(
    research_params: ResearchParams,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Create a research."""
    if research_params.business_id is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail='Create research for general knowledge is not implemented yet.',
        )
    else:
        business_id = research_params.business_id
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
        if research_params.sync_generation:
            research = deep_research_for_business(
                business=business,
                params=research_params,
            )
        else:
            research = deep_research_for_business_async(
                business=business,
                params=research_params,
            )
    return research


@router.post(
    '/store',
    summary='Store research',
    response_model=Research,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def store_research(
    research_params: ResearchStoreParams,
):
    """Store research."""
    if research_params.research_id is not None:
        research_info = get_deep_research_async(
            request_id=research_params.research_id,
        )
        if research_info.status is not ResearchRequestStatusEnum.COMPLETED:
            research_status = (
                research_info.status.value if research_info.status else 'unknown'
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    'Research request is not completed yet. Current status is '
                    f'{research_status}'
                ),
            )
        research_text = research_info.research
    elif research_params.research is not None:
        research_text = research_params.research
    else:
        raise ValueError(
            'Either research_id or research must be provided. This error should never '
            'happen, as it is handled by the schema validator.'
        )
    chunk_and_upload_text(
        text=research_text,
        business_id=research_params.business_id,
    )
    return Research(research=research_text)
