"""API endpoints for user management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker
from app.deps import get_current_active_user, get_repository
from app.domain import UserBase as UserBaseDomain
from app.enums import UserRoleEnum
from app.repositories import UserRepository
from app.schemas import User, UserCreate

router = APIRouter(
    tags=['User'],
    prefix='/users',
)


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
    current_user: User = Depends(get_current_active_user),
):
    """Get information about the current user."""
    return current_user


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
    existing_user = await users_repo.get_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists',
        )
    user_to_create = UserBaseDomain(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        password=user.password.get_secret_value(),
        role=user.role,
    )
    return await users_repo.create(user_to_create)
