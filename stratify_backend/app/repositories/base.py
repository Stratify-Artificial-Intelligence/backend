from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base


class BaseRepository:
    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self._db = db

    async def commit(self):
        try:
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise

    @staticmethod
    def update_model(model: Base, update: dict[str, Any]):
        for field, value in update.items():
            setattr(model, field, value)
        return model
