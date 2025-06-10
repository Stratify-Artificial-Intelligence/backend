"""API endpoints for plan management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.authorization_server import RoleChecker
from app.deps import get_repository
from app.domain import PlanBase as PlanBaseDomain
from app.enums import UserRoleEnum
from app.repositories import PlanRepository
from app.schemas import Plan, PlanPartialUpdate

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
    '',
    summary='Create a new plan',
    status_code=status.HTTP_201_CREATED,
    response_model=Plan,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def create_plan(
    plan: Plan,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """Create a new plan."""
    plan_to_create = PlanBaseDomain.model_validate(plan)
    return await plans_repo.create(plan_to_create)


@router.patch(
    '/{plan_id}',
    summary='Update a plan',
    status_code=status.HTTP_200_OK,
    response_model=Plan,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def partial_update_plan(
    plan_id: int,
    plan_data: PlanPartialUpdate,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """Update a plan."""
    plan = await plans_repo.get(plan_id=plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Plan not found',
        )
    update_data = plan_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    return await plans_repo.update(plan_id, plan)


@router.delete(
    '/{plan_id}',
    summary='Delete a plan',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
    dependencies=[Depends(RoleChecker(allowed_roles=[UserRoleEnum.ADMIN]))],
)
async def delete_plan(
    plan_id: int,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """Delete a plan."""
    plan = await plans_repo.get(plan_id=plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Plan not found',
        )
    await plans_repo.delete(plan_id)
    return None
