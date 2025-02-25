from typing import AsyncGenerator, Callable

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import async_session, engine
from app.main import app


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    # async with engine.begin() as connection:
    async with async_session() as session:
        yield session
        await session.flush()
        await session.rollback()


@pytest.fixture()
def override_get_db(db_session: AsyncSession) -> Callable:
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as ac:
        yield ac
