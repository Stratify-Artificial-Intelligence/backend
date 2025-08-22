"""API endpoints for business research management."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

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
from app.schemas import ResearchExtended, ResearchParams, ResearchStoreById

router = APIRouter(
    tags=['Research'],
    prefix='/researches',
)


@router.get(
    '/{research_id}',
    summary='Get research by ID',
    response_model=ResearchExtended,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[
        Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN, UserRoleEnum.SERVICE]))
    ],
)
async def get_research_by_id(
    research_id: str,
):
    """Get research by ID."""
    # ToDo (pduran): Implement authorization check for research access. This would
    #  require to store the mapping of research IDs to business IDs or user IDs, which
    #  is not currently implemented.
    research = get_deep_research_async(request_id=research_id)
    if research is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Research not found',
        )
    return research


@router.post(
    '/{research_id}/store',
    summary='Store research by ID',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[
        Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN, UserRoleEnum.SERVICE]))
    ],
)
async def store_research_by_id(  # noqa: C901
    research_id: str,
    research_store_params: ResearchStoreById,
):
    """Store research by ID."""
    research_info = get_deep_research_async(request_id=research_id)
    if research_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Research not found',
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
    if research_info.research is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f'Research text empty (although status is {research_info.status}).',
            ),
        )
    research_text = research_info.research
    chunk_and_upload_text(
        text=research_text,
        business_id=research_store_params.business_id,
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
    dependencies=[
        Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN, UserRoleEnum.BASIC])),
    ],
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
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def store_research(  # noqa: C901
    business_id: int | None = Form(None),
    research: str | None = Form(None),
    research_file: UploadFile | None = File(None),
):
    """Store research."""
    fields_set = [field for field in [research, research_file] if field is not None]
    if len(fields_set) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Exactly one of research, or research_file must be provided.',
        )

    if research is not None:
        research_text = research
    elif research_file is not None:
        if research_file.filename is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Filename is required for research_file.',
            )
        if not research_file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Only .txt files are supported for research_file.',
            )
        contents = await research_file.read()
        try:
            research_text = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Uploaded file must be UTF-8 encoded.',
            )
    else:
        raise ValueError(
            'Either research_id or research must be provided. This error should never '
            'happen.'
        )

    chunk_and_upload_text(text=research_text, business_id=business_id)
