from app.enums import BusinessStageEnum
from app.models import Business, BusinessIdea, EstablishedBusiness
from app.domain import (
    Business as BusinessDomain,
    BusinessIdea as BusinessIdeaDomain,
    EstablishedBusiness as EstablishedBusinessDomain,
)
from app.repositories import BaseRepository

from sqlalchemy import select


class BusinessRepository(BaseRepository):
    async def get(self, business_id: int) -> BusinessDomain | None:
        business = await self._get(business_id=business_id)
        if business is None:
            return None
        return BusinessDomain.model_validate(business)

    async def create_idea(self, business_in: BusinessIdeaDomain) -> BusinessIdeaDomain:
        new_business_idea = BusinessIdea(
            name=business_in.name,
            location=business_in.location,
            description=business_in.description,
            goal=business_in.goal,
            stage=business_in.stage,
            team_size=business_in.team_size,
            team_description=business_in.team_description,
            user_id=business_in.user_id,
            competitor_existence=business_in.competitor_existence,
            competitor_differentiation=business_in.competitor_differentiation,
            investment=business_in.investment,
            investment_currency=business_in.investment_currency,
        )
        self._db.add(new_business_idea)
        await self.commit()
        await self._db.refresh(new_business_idea)
        return BusinessIdeaDomain.model_validate(new_business_idea)

    async def create_established(
        self,
        business_in: EstablishedBusinessDomain,
    ) -> EstablishedBusinessDomain:
        new_established_business = EstablishedBusiness(
            name=business_in.name,
            location=business_in.location,
            description=business_in.description,
            goal=business_in.goal,
            stage=business_in.stage,
            team_size=business_in.team_size,
            team_description=business_in.team_description,
            user_id=business_in.user_id,
            billing=business_in.billing,
            billling_currency=business_in.billing_currency,
            ebitda=business_in.ebitda,
            ebitda_currency=business_in.ebitda_currency,
            profit_margin=business_in.profit_margin,
        )
        self._db.add(new_established_business)
        await self.commit()
        await self._db.refresh(new_established_business)
        return EstablishedBusinessDomain.model_validate(new_established_business)

    async def _get(self, business_id: int) -> Business | None:
        query = select(Business).where(Business.id == business_id)
        result = await self._db.execute(query)
        return result.scalars().one_or_none()
