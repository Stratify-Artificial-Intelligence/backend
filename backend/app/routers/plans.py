"""API endpoints for plan management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.deps import get_current_active_user, get_repository
from app.domain import User as UserDomain
from app.helpers import create_subscription_and_update_user
from app.repositories import PlanRepository, UserRepository
from app.schemas import Plan, PlanSubscriptionResponse

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


@router.post(
    '{plan_id}/subscribe',
    summary='Subscribe to a plan',
    status_code=status.HTTP_200_OK,
    response_model=PlanSubscriptionResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def subscribe_to_plan(
    plan_id: int,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Subscribe user to a plan."""
    plan = await plans_repo.get(plan_id=plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Plan not found',
        )
    return await create_subscription_and_update_user(
        user=current_user,
        plan=plan,
        users_repo=users_repo,
    )
