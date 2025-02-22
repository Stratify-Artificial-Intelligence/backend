from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


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
