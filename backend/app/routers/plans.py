"""API endpoints for plan management."""

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.deps import get_repository
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
    response_model=SubscriptionResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
        status.HTTP_403_FORBIDDEN: {'model': schemas.HTTP403Forbidden},
        status.HTTP_404_NOT_FOUND: {'model': schemas.HTTP404NotFound},
    },
)
async def subscribe_to_plan(
    plan_id: int,
    plans_repo: PlanRepository = Depends(get_repository(PlanRepository)),
    current_user: UserDomain = Depends(get_current_active_user),
):
    """Subscribe to a plan."""
    plan = await plans_repo.get(plan_id=plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Plan not found',
        )

    try:
        # Create or retrieve Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(email=user.email)
            user.stripe_customer_id = customer.id
        else:
            customer = stripe.Customer.retrieve(user.stripe_customer_id)

        # Cancel existing subscription if any
        if user.stripe_subscription_id:
            stripe.Subscription.delete(user.stripe_subscription_id)

        # Create new subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": plan.price_id}],
            expand=["latest_invoice.payment_intent"]
        )

        # Save subscription ID only — wait for webhook to update plan_id
        user.stripe_subscription_id = subscription.id
        db.commit()

        # Return client secret for frontend confirmation
        return {
            "message": "Subscription created, waiting for payment confirmation",
            "client_secret": subscription["latest_invoice"]["payment_intent"][
                "client_secret"]
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

