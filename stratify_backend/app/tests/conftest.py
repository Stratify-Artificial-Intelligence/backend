from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


# @pytest.fixture(scope='session')
# def event_loop(request) -> Generator:
#     """Create an instance of the default event loop for each test case."""
#     # ToDo (pduran): This seems to not work as expected
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# @pytest_asyncio.fixture(scope="session", autouse=True)
# async def setup_test_db():
#     """Create and drop tables before/after tests."""
#     async with engine.begin() as connection:
#         await connection.run_sync(Base.metadata.create_all)
#         yield
#         await connection.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture
# async def db_session() -> AsyncGenerator[AsyncSession, None]:
#     async for session in get_session():
#         yield session
#         await session.rollback()


# @pytest.fixture(scope="function")
# def override_get_db(db_session: AsyncSession) -> Callable:
#     """Override FastAPI's get_db dependency."""
#     async def _override_get_db():
#         yield db_session
#
#     return _override_get_db


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
