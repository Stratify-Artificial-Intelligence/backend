from app.models import Test
from app.domain import Test as TestDomain
from app.repositories import BaseRepository

from sqlalchemy import delete, select


class TestRepository(BaseRepository):
    async def get(self, test_id: int) -> TestDomain | None:
        test = await self._get(test_id=test_id)
        if test is None:
            return None
        return TestDomain.model_validate(test)

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

    async def update(self, test_id: int, test_update: TestDomain) -> TestDomain | None:
        test = await self._get(test_id=test_id)
        if test is None:
            return None

        self.update_model(model=test, update=test_update.model_dump(exclude_unset=True))

        await self._db.commit()
        await self._db.refresh(test)
        return TestDomain.model_validate(test)

    async def delete(self, test_id: int) -> None:
        query = delete(Test).where(Test.id == test_id)
        await self._db.execute(query)
        await self.commit()

    async def _get(self, test_id: int) -> Test | None:
        query = select(Test).where(Test.id == test_id)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()
