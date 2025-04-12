"""API endpoints for business management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import user_can_read_business
from app.deps import get_current_active_user, get_repository
from app.domain import (
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
    User as UserDomain,
)
from app.enums import BusinessStageEnum
from app.repositories import BusinessRepository
from app.schemas import (
    BusinessIdea,
    BusinessIdeaBase,
    EstablishedBusiness,
    EstablishedBusinessBase,
)

router = APIRouter(
    tags=['Business'],
    prefix='/businesses',
)


# @router.get(
#     '',
#     summary='List businesses',
#     response_model=list[ChatBase],
#     responses={
#         status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
#     },
# )
# async def list_businesses(
#     chats_repo: ChatRepository = Depends(get_repository(ChatRepository)),
#     current_user: UserDomain = Depends(get_current_active_user),
# ):
#     """List all businesses accessible by the current user."""
#     return await chats_repo.get_multi(user_id=current_user.id)


@router.get(
    '/{business_id}',
    summary='Get business by ID',
    response_model=BusinessIdea | EstablishedBusiness,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def get_business_by_id(
    business_id: int,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Get a specific business by ID."""
    business = await business_repo.get(business_id=business_id)
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
    return business


@router.post(
    '/ideas',
    summary='Create business idea',
    response_model=BusinessIdea,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def create_business_idea(
    business_in: BusinessIdeaBase,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Create a new business idea."""
    business_idea = BusinessIdeaDomain(
        **{
            **business_in.model_dump(),
            'user_id': current_user.id,
            'stage': BusinessStageEnum.IDEA,
        }
    )
    return await business_repo.create_idea(business_idea)


@router.post(
    '/established',
    summary='Create established business',
    response_model=EstablishedBusiness,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def create_established_business(
    business_in: EstablishedBusinessBase,
    business_repo: BusinessRepository = Depends(get_repository(BusinessRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Create a new established business."""
    established_business = EstablishedBusinessDomain(
        **{
            **business_in.model_dump(),
            'user_id': current_user.id,
            'stage': BusinessStageEnum.ESTABLISHED,
        }
    )
    return await business_repo.create_established(established_business)
