from sqlalchemy import select

from app.domain import User as UserDomain
from app.models import User
from app.repositories import BaseRepository
from app.security import get_password_hash, verify_password


class UserRepository(BaseRepository):
    async def get_by_username(self, username: str) -> UserDomain | None:
        query = select(User).where(User.username == username)
        result = await self._db.execute(query)
        user = result.scalars().one_or_none()
        if user is None:
            return None
        return UserDomain.model_validate(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'password': user.hashed_password,
            }
        )

    async def get_multi(self) -> list[UserDomain]:
        query = select(User)
        result = await self._db.execute(query)
        users = result.scalars().all()
        return [
            UserDomain.model_validate(
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'password': user.hashed_password,
                }
            )
            for user in users
        ]

    async def create(self, user_in: UserDomain) -> UserDomain:
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            username=user_in.username,
            hashed_password=hashed_password,
            email=user_in.email,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
        )
        self._db.add(new_user)
        await self.commit()
        await self._db.refresh(new_user)
        return UserDomain.model_validate(
            {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'full_name': new_user.full_name,
                'is_active': new_user.is_active,
                'password': new_user.hashed_password,
            }
        )

    async def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> UserDomain | None:
        user = await self.get_by_username(username)
        if not user:
            return None
        if not verify_password(plain_password=password, hashed_password=user.password):
            return None
        return user
