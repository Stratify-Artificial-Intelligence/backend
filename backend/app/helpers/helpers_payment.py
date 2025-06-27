import logging

from fastapi import HTTPException, Request, status

from app.domain import Plan as PlanDomain, User as UserDomain
from app.repositories import PlanRepository, UserRepository
from app.schemas import (
    CheckoutSession,
    CheckoutSessionResponse,
    SubscriptionHandleRequest,
    SubscriptionHandleResponse,
)
from app.services.stripe import (
    create_checkout_session as stripe_create_checkout_session,
    create_customer,
    get_checkout_session as stripe_get_checkout_session,
    get_portal_session as stripe_get_portal_session,
    get_subscription,
    verify_webhook_signature,
)


logger = logging.getLogger(__name__)


async def get_checkout_session(session_id: str) -> CheckoutSessionResponse | None:
    session = await stripe_get_checkout_session(session_id)
    if session is None:
        return None
    if not isinstance(session.customer, str):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Checkout session does not have a valid customer.',
        )
    if not isinstance(session.subscription, str):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Checkout session does not have a valid subscription.',
        )
    return CheckoutSessionResponse(
        customer=session.customer,
        status=session.payment_status,
        subscription=session.subscription,
    )


async def create_checkout_session(
    plan: PlanDomain,
    user: UserDomain,
    success_url: str,
    cancel_url: str,
    users_repo: UserRepository,
) -> CheckoutSession:
    """Create a checkout session for the given plan."""
    if plan.payment_service_price_id is None:
        raise ValueError(
            f'Plan {plan.id} does not have a payment service price ID. Cannot create '
            f'checkout session.'
        )
    customer_id = await get_or_create_customer(user=user, users_repo=users_repo)
    session = await stripe_create_checkout_session(
        success_url=success_url,
        cancel_url=cancel_url,
        price_id=plan.payment_service_price_id,
        customer_id=customer_id,
    )
    if session.url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create checkout session. No URL returned.',
        )

    return CheckoutSession(url=session.url)


async def get_or_create_customer(user: UserDomain, users_repo: UserRepository) -> str:
    if user.payment_service_user_id is None:
        customer = await create_customer(email=user.email, name=user.full_name)
        customer_id = customer.id
        user.payment_service_user_id = customer_id
        await users_repo.update(user_id=user.id, user_update=user)
        return customer_id
    else:
        return user.payment_service_user_id


async def get_portal_session(user: UserDomain, data: SubscriptionHandleRequest):
    if user.payment_service_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User does not have a payment service user ID.',
        )
    session = await stripe_get_portal_session(
        customer_id=user.payment_service_user_id,
        return_url=data.return_url,
    )
    return SubscriptionHandleResponse(url=session.url)


async def handle_subscription_webhook(
    request: Request,
    users_repo: UserRepository,
    plans_repo: PlanRepository,
) -> None:
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    if sig_header is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Missing Stripe signature header.',
        )

    try:
        event = await verify_webhook_signature(payload, sig_header)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid signature',
        ) from e
    if event.type == 'checkout.session.completed':
        object = event.data.object
        logger.info(f'Handle subscription webhook object {object}')

        customer_id = object.get('customer')
        users = await users_repo.get_multi(payment_service_user_id=customer_id)
        if len(users) != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found for the given customer ID.',
            )
        user = users[0]

        subscription_id = object.get('subscription')
        if subscription_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Subscription ID not found in the webhook object.',
            )
        subscription = await get_subscription(subscription_id=subscription_id)
        stripe_price_id = subscription['items']['data'][0]['price']['id']
        plans = await plans_repo.get_multi(payment_service_price_id=stripe_price_id)
        if len(plans) != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Plan not found for the given Stripe price ID.',
            )
        plan = plans[0]

        user.plan_id = plan.id
        await users_repo.update(user_id=user.id, user_update=user)
