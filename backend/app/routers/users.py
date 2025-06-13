"""API endpoints for user management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker
from app.deps import get_current_active_user, get_repository
from app.domain import User as UserDomain, UserWithSecret as UserWithSecretDomain
from app.enums import UserRoleEnum
from app.helpers import create_user_in_auth_service
from app.repositories import UserRepository
from app.schemas import (
    User,
    UserBaseCreate,
    UserPartialUpdate,
    UserCreate,
    UserMePartialUpdate,
)

router = APIRouter(
    tags=['User'],
    prefix='/users',
)


@router.post(
    '/signup',
    summary='Register a new user',
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
    },
)
async def signup_user(
    user: UserBaseCreate,
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Sign up a new user."""
    if user.password is not None:
        external_id = create_user_in_auth_service(
            email=user.email,
            password=user.password.get_secret_value(),
        )
    else:
        external_id = user.external_id
    user_to_create = UserWithSecretDomain(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
        external_id=external_id,
        role=UserRoleEnum.BASIC,
    )
    try:
        user_created = await users_repo.create(user_to_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user_created


@router.get(
    '/me',
    summary='Info about me',
    status_code=status.HTTP_200_OK,
    response_model=User,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def read_users_me(
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Get information about the current user."""
    return current_user


@router.patch(
    '/me',
    summary='Partial update me',
    status_code=status.HTTP_200_OK,
    response_model=User,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def update_users_me(
    user_data: UserMePartialUpdate,
    current_user: UserDomain = Depends(get_current_active_user),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Update user information."""
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
    try:
        user_updated = await users_repo.update(current_user.id, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user_updated


@router.get(
    '',
    summary='List users',
    status_code=status.HTTP_200_OK,
    response_model=list[User],
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def list_users(
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """List of all users present in the database."""
    return await users_repo.get_multi()


@router.get(
    '/{user_id}',
    summary='Get user by ID',
    status_code=status.HTTP_200_OK,
    response_model=User,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def get_user_by_id(
    user_id: int,
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Get user by ID."""
    user = await users_repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    return user


@router.post(
    '',
    summary='Create user',
    status_code=status.HTTP_201_CREATED,
    response_model=User,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def create_user(
    user: UserCreate,
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Create a new user."""
    user_to_create = UserWithSecretDomain(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        external_id=user.password.get_secret_value(),
        role=user.role,
    )
    try:
        user_created = await users_repo.create(user_to_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user_created


@router.patch(
    '/{user_id}',
    summary='Partial update user',
    status_code=status.HTTP_200_OK,
    response_model=User,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def update_user(
    user_id: int,
    user_data: UserPartialUpdate,
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Update user information."""
    user = await users_repo.get(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    try:
        user_updated = await users_repo.update(user_id, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user_updated
