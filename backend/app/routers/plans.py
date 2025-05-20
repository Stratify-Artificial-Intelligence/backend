"""API endpoints for plan management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker
from app.deps import get_repository
from app.enums import UserRoleEnum
from app.repositories import PlanRepository
from app.schemas import Plan

router = APIRouter(
    tags=['Plan'],
    prefix='/plans',
)


@router.get(
    '',
    summary='List plans',
    status_code=status.HTTP_200_OK,
    response_model=list[Plan],
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def list_plans(
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """List of all plans present in the database."""
    return await plans_repo.get_multi()


@router.get(
    '/{plan_id}',
    summary='Get plan by ID',
    status_code=status.HTTP_200_OK,
    response_model=Plan,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def get_plan_by_id(
    plan_id: int,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """Get plan by ID."""
    plan = await plans_repo.get(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Plan not found',
        )
    return plan
