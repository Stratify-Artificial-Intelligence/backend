from app.models import Test
from app.domain import Test as TestDomain
from app.repositories import BaseRepository

from sqlalchemy import select


class TestRepository(BaseRepository):
    async def get_multi(self) -> list[TestDomain]:
        query = select(Test)
        result = await self._db.execute(query)
        tests = result.scalars().all()
        return [TestDomain.model_validate(test) for test in tests]

    async def create(self, test_in: TestDomain) -> TestDomain:
        new_test = Test(name=test_in.name, description=test_in.description)
        self._db.add(new_test)
        await self.commit()
        await self._db.refresh(new_test)
        return TestDomain.model_validate(new_test)
