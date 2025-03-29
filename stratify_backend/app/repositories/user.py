from sqlalchemy import select

from app.domain import (
    User as UserDomain,
    UserBase as UserBaseDomain,
    UserWithSecret as UserWithSecretDomain,
)
from app.models import User
from app.repositories import BaseRepository
from app.security import get_password_hash, verify_password


class UserRepository(BaseRepository):
    async def get(self, user_id: int) -> UserDomain | None:
        query = select(User).where(User.id == user_id)
        result = await self._db.execute(query)
        user = result.scalars().one_or_none()
        if user is None:
            return None
        return await self._user_model_to_domain(user)

    async def get_by_username(self, username: str) -> UserDomain | None:
        query = select(User).where(User.username == username)
        result = await self._db.execute(query)
        user = result.scalars().one_or_none()
        if user is None:
            return None
        return await self._user_model_to_domain(user)

    async def get_multi(self) -> list[UserDomain]:
        query = select(User)
        result = await self._db.execute(query)
        users = result.scalars().all()
        return [await self._user_model_to_domain(user) for user in users]

    async def create(self, user_in: UserWithSecretDomain) -> UserDomain:
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            username=user_in.username,
            hashed_password=hashed_password,
            email=user_in.email,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            role=user_in.role,
        )
        self._db.add(new_user)
        await self.commit()
        await self._db.refresh(new_user)
        return await self._user_model_to_domain(new_user)

    async def update(
        self,
        user_id: int,
        user_update: UserBaseDomain | UserWithSecretDomain,
    ) -> UserDomain | None:
        user = await self._get(user_id)
        if user is None:
            return None

        user_dict = user_update.model_dump(exclude_unset=True)
        try:
            user_dict['hashed_password'] = get_password_hash(user_dict['password'])
        except KeyError:
            pass

        self.update_model(model=user, update=user_dict)

        await self.commit()
        await self._db.refresh(user)
        return await self._user_model_to_domain(user)

    async def _get(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()

    @staticmethod
    async def _user_model_to_domain(user: User) -> UserDomain:
        return UserDomain.model_validate(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'password': user.hashed_password,
                'role': user.role,
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
