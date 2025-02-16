# mypy: ignore-errors

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.settings import PostgresSettings

settings = PostgresSettings()

Base = declarative_base()

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=True,
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
