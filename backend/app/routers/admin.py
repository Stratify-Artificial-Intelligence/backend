"""API endpoints for admin management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker
from app.deps import get_current_active_user, get_repository
from app.domain import UserExtended as UserExtendedDomain
from app.enums import UserRoleEnum
from app.repositories import UserRepository
from app.schemas import Token
from app.services import ServicesFactory

router = APIRouter(
    tags=['Admin'],
    prefix='',
)


@router.post(
    '/token/view_as/{user_id}',
    summary='Generate impersonation token',
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def token_view_as_user(
    user_id: int,
    current_user: UserExtendedDomain = Depends(get_current_active_user),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Retrieve an impersonation token for a specific user."""
    impersonated_user = await users_repo.get(user_id)
    if impersonated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    if impersonated_user.role == UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Cannot impersonate another admin user',
        )
    identity_service = ServicesFactory().get_identity_provider()
    if current_user.external_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                'Current user does not have an external ID. Thus, it cannot impersonate.'
            ),
        )
    if impersonated_user.external_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                'Impersonated user does not have an external ID. Thus, it cannot be '
                'impersonated.'
            ),
        )
    token_str = identity_service.generate_impersonation_token(
        original_sub=current_user.external_id,
        impersonated_sub=impersonated_user.external_id,
    )
    return Token(access_token=token_str, token_type='Bearer')
