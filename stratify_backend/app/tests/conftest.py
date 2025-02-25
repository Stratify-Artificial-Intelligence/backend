from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgresql import get_session
from app.main import app


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',
    ) as ac:
        yield ac


def pytest_collection_modifyitems(items):
    """Add a marker to tests depending on integration or unit.

    See also
    --------
    pytest.ini markers
    """
    for item in items:
        item_path = str(item.path)
        if 'tests/integration/' in item_path:
            item.add_marker(pytest.mark.integration)
        elif 'tests/unit/' in item_path:
            item.add_marker(pytest.mark.unit)
