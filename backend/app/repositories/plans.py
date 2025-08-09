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

    async def get_multi(
        self,
        *,
        name: str | None = None,
        is_active: bool | None = None,
        payment_service_price_id: str | None = None,
    ) -> list[PlanDomain]:
        query = select(Plan)
        if name is not None:
            query = query.where(Plan.name == name)
        if is_active is not None:
            query = query.where(Plan.is_active == is_active)
        if payment_service_price_id is not None:
            query = query.where(
                Plan.payment_service_price_id == payment_service_price_id
            )
        result = await self._db.execute(query)
        plans = result.scalars().all()
        return [PlanDomain.model_validate(plan) for plan in plans]

    async def create(self, plan_in: PlanBaseDomain) -> PlanDomain:
        new_plan = Plan(
            name=plan_in.name,
            is_active=plan_in.is_active,
            price=plan_in.price,
            payment_service_price_id=plan_in.payment_service_price_id,
            monthly_credits=plan_in.monthly_credits,
        )
        self._db.add(new_plan)
        await self.commit()
        await self._db.refresh(new_plan)
        return PlanDomain.model_validate(new_plan)

    async def update(self, plan_id: int, plan_in: PlanBaseDomain) -> PlanDomain | None:
        plan = await self._get(plan_id=plan_id)
        if not plan:
            return None

        for attr, value in plan_in.model_dump().items():
            setattr(plan, attr, value)

        await self.commit()
        await self._db.refresh(plan)
        return PlanDomain.model_validate(plan)

    async def delete(self, plan_id: int) -> None:
        plan = await self._get(plan_id=plan_id)
        if not plan:
            return None

        await self._db.delete(plan)
        await self.commit()
        return None

    async def _get(self, plan_id: int) -> Plan | None:
        query = select(Plan).where(Plan.id == plan_id)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()
