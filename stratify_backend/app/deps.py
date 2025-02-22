from typing import Callable, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_session
from app.repositories import BaseRepository


def get_repository(repo_type: Type[BaseRepository]) -> Callable:
    def _get_repo(db: AsyncSession = Depends(get_session)) -> BaseRepository:
        return repo_type(db)

    return _get_repo
