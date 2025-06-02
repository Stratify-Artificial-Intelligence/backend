from sqlalchemy import select

from app.domain import Plan as PlanDomain, PlanBase as PlanBaseDomain
from app.models.plan import Plan
from app.repositories import BaseRepository


class PlanRepository(BaseRepository):
    async def get(self, plan_id: int) -> PlanDomain | None:
        plan = await self._get(plan_id=plan_id)
        if plan is None:
            return None
        return PlanDomain.model_validate(plan)

    async def get_multi(self) -> list[PlanDomain]:
        query = select(Plan)
        result = await self._db.execute(query)
        plans = result.scalars().all()
        return [PlanDomain.model_validate(plan) for plan in plans]

    async def create(self, plan_in: PlanBaseDomain) -> PlanDomain:
        new_plan = Plan(
            name=plan_in.name,
            is_active=plan_in.is_active,
        )
        self._db.add(new_plan)
        await self.commit()
        await self._db.refresh(new_plan)
        return PlanDomain.model_validate(new_plan)

    async def _get(self, plan_id: int) -> Plan | None:
        query = select(Plan).where(Plan.id == plan_id)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()
