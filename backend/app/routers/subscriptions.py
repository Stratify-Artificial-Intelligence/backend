"""API endpoints for subscription management."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app import schemas
from app.deps import get_current_active_user, get_repository
from app.domain import User as UserDomain
from app.helpers import (
    create_checkout_session,
    get_checkout_session,
    get_portal_session,
    handle_subscription_webhook,
)
from app.repositories import PlanRepository, UserRepository
from app.schemas import (
    CheckoutSession,
    CheckoutSessionResponse,
    SubscriptionCreation,
    SubscriptionHandleRequest,
    SubscriptionHandleResponse,
)

router = APIRouter(
    tags=['Subscription'],
    prefix='/subscriptions',
)


@router.get(
    '/{session_id}',
    summary='Get a subscription session by ID',
    status_code=status.HTTP_200_OK,
    response_model=CheckoutSessionResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def get_subscription(session_id: str):
    """Get a subscription session by its ID."""
    response = await get_checkout_session(session_id=session_id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Session {session_id} not found',
        )
    return response


@router.post(
    '',
    summary='Create subscription',
    status_code=status.HTTP_201_CREATED,
    response_model=CheckoutSession,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
    },
)
async def create_subscription(
    subscription_data: SubscriptionCreation,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """Subscribe user to a plan."""
    plan = await plans_repo.get(plan_id=subscription_data.plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Plan not found.',
        )
    return await create_checkout_session(
        plan=plan,
        success_url=subscription_data.success_url,
        cancel_url=subscription_data.cancel_url,
    )


@router.post(
    '/handle',
    summary='Handle subscription',
    status_code=status.HTTP_200_OK,
    response_model=SubscriptionHandleResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def create_portal_session(
    request_data: SubscriptionHandleRequest,
    current_user: UserDomain = Depends(get_current_active_user),
):
    return await get_portal_session(user=current_user, data=request_data)


@router.post(
    '/webhook',
    summary='Webhook for subscription events',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {'model': schemas.HTTP400BadRequest},
    },
    include_in_schema=False,
)
async def subscription_webhook(
    request: Request,
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
):
    """Subscriptions webhook."""
    return await handle_subscription_webhook(
        request=request,
        users_repo=users_repo,
        plans_repo=plans_repo,
    )
