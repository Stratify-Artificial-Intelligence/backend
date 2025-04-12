from fastapi import Depends, HTTPException, status

from app.deps import get_current_active_user
from app.domain import Business as BusinessDomain, Chat as ChatDomain, User as UserDomain


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        current_user: UserDomain = Depends(get_current_active_user),
    ):
        if current_user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User does not have enough privileges.',
        )


def user_can_read_business(business: BusinessDomain, user: UserDomain) -> bool:
    return business.user_id == user.id


def user_can_read_chat(business: BusinessDomain, user: UserDomain) -> bool:
    return business.user_id == user.id


def user_can_create_chat(business: BusinessDomain, user: UserDomain) -> bool:
    return business.user_id == user.id


def user_can_publish_message(business: BusinessDomain, user: UserDomain) -> bool:
    return business.user_id == user.id
