from sqlalchemy import select

from app.domain import (
    User as UserDomain,
    UserBase as UserBaseDomain,
    UserWithSecret as UserWithSecretDomain,
)
from app.models import User
from app.repositories import BaseRepository


class UserRepository(BaseRepository):
    async def get(self, user_id: int) -> UserDomain | None:
        query = select(User).where(User.id == user_id)
        result = await self._db.execute(query)
        user = result.scalars().one_or_none()
        if user is None:
            return None
        return await self._user_model_to_domain(user)

    async def get_by_username(self, username: str) -> UserDomain | None:
        user = await self._get_by_username(username=username)
        if user is None:
            return None
        return await self._user_model_to_domain(user)

    async def get_by_email(self, email: str) -> UserDomain | None:
        user = await self._get_by_email(email=email)
        if user is None:
            return None
        return await self._user_model_to_domain(user)

    async def get_by_external_id(self, external_id: str) -> UserDomain | None:
        user = await self._get_by_external_id(external_id=external_id)
        if user is None:
            return None
        return await self._user_model_to_domain(user)

    async def get_multi(
        self,
        *,
        payment_service_user_id: str | None = None,
    ) -> list[UserDomain]:
        query = select(User)
        if payment_service_user_id is not None:
            query = query.where(User.payment_service_user_id == payment_service_user_id)
        result = await self._db.execute(query)
        users = result.scalars().all()
        return [await self._user_model_to_domain(user) for user in users]

    async def create(self, user_in: UserWithSecretDomain) -> UserDomain:
        if await self.get_by_username(username=user_in.username):
            raise ValueError('Username already exists')
        if await self.get_by_email(email=user_in.email):
            raise ValueError('Email already exists')
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            full_name=user_in.full_name,
            external_id=user_in.external_id,
            is_active=user_in.is_active,
            role=user_in.role,
            language=user_in.language,
            plan_id=user_in.plan_id,
            available_credits=user_in.available_credits,
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
            username = user_dict['username']
            existing_user = await self.get_by_username(username)
            if existing_user and existing_user.id != user_id:
                raise ValueError('Username already exists')
        except KeyError:
            pass

        try:
            email = user_dict['email']
            existing_user = await self.get_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValueError('Email already exists')
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

    async def _get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()

    async def _get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()

    async def _get_by_external_id(self, external_id: str) -> User | None:
        query = select(User).where(User.external_id == external_id)
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
                'role': user.role,
                'language': user.language,
                'plan_id': user.plan_id,
                'payment_service_user_id': user.payment_service_user_id,
                'available_credits': user.available_credits,
            }
        )
