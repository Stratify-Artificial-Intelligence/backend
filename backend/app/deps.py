from typing import Callable, Type

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_session
from app.domain import (
    Business as BusinessDomain,
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
    User as UserDomain,
)
from app.helpers import check_auth_token
from app.repositories import BaseRepository, BusinessRepository, UserRepository
from app.schemas import TokenData


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def _get_repo(db: AsyncSession = Depends(get_session)) -> BaseRepository:
        return repo_type(db)

    return _get_repo


async def get_current_user(
    token_data: TokenData = Depends(check_auth_token),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserDomain:
    user = await users_repo.get_by_external_id(external_id=token_data.user_external_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        )
    return user


async def get_current_active_user(
    current_user: UserDomain = Depends(get_current_user),
) -> UserDomain:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user',
        )
    return current_user


async def get_business(
    business_id: int,
    user: UserDomain,
    business_repo: BusinessRepository,
    permission_func: Callable[[BusinessDomain, UserDomain], bool],
    load_hierarchy: bool = False,
) -> BusinessDomain | BusinessIdeaDomain | EstablishedBusinessDomain:
    business = (
        await business_repo.get_child(business_id=business_id)
        if load_hierarchy
        else await business_repo.get(business_id=business_id)
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Business not found',
        )
    if not permission_func(business, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not have enough privileges.',
        )
    return business
