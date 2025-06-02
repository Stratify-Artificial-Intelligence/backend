from app.domain import Plan as PlanDomain, User as UserDomain
from app.repositories import UserRepository
from app.schemas import PaymentMethodResponse, PlanSubscriptionResponse
from app.services.stripe import (
    cancel_subscription,
    create_client_intent,
    create_customer,
    create_subscription,
    get_customer,
    setup_client_intent,
)


async def create_payment_method(
    user: UserDomain,
    users_repo: UserRepository,
) -> PaymentMethodResponse:
    """Create a payment method for the user."""
    customer_id = await _get_or_create_customer_id(user, users_repo)
    client_intent = await create_client_intent(customer_id)
    if client_intent.client_secret is None:
        raise ValueError(
            'Failed to create client intent for payment method. Client secret returned '
            'by Stripe is None.'
        )
    return PaymentMethodResponse(
        id=client_intent.id,
        client_secret=client_intent.client_secret,
    )


async def setup_payment_method(
    payment_method_id: str,
    user: UserDomain,
    users_repo: UserRepository,
) -> None:
    """Set up a payment method for the user."""
    customer_id = await _get_or_create_customer_id(user, users_repo)
    await setup_client_intent(customer_id, payment_method_id)


async def create_subscription_and_update_user(
    user: UserDomain,
    plan: PlanDomain,
    users_repo: UserRepository,
) -> PlanSubscriptionResponse:
    """Create a subscription for the user and update the user with its ID."""
    customer_id = await _get_or_create_customer_id(user, users_repo)
    await cancel_subscription_and_update_user(user, users_repo)
    if plan.payment_service_price_id is None:
        raise ValueError(
            'Plan does not have a payment service price ID. Cannot create subscription.'
        )
    subscription = await create_subscription(customer_id, plan.payment_service_price_id)
    user.payment_service_subscription_id = subscription.id
    await users_repo.update(user_id=user.id, user_update=user)
    return PlanSubscriptionResponse(
        id=subscription.id,
        payment_client_secret=(
            subscription['latest_invoice']['payment_intent']['client_secret']
        ),
    )


async def cancel_subscription_and_update_user(
    user: UserDomain,
    users_repo: UserRepository,
) -> None:
    """Cancel the user's subscription and update the user."""
    if user.payment_service_subscription_id is None:
        return
    await cancel_subscription(subscription_id=user.payment_service_subscription_id)
    user.payment_service_subscription_id = None
    await users_repo.update(user_id=user.id, user_update=user)


async def _get_or_create_customer_id(
    user: UserDomain,
    users_repo: UserRepository,
) -> str:
    if user.payment_service_user_id is None:
        customer = await create_customer(email=user.email)
        user.payment_service_user_id = customer.id
        await users_repo.update(user_id=user.id, user_update=user)
    else:
        customer = await get_customer(customer_id=user.payment_service_user_id)
    return customer.id
