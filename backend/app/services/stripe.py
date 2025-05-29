import stripe

from app.domain import Plan as PlanDomain, User as UserDomain
from app.repositories import UserRepository


async def get_or_create_user_id(
    user: UserDomain,
    user_repo: UserRepository,
) -> str:
    if user.payment_service_user_id is None:
        customer = stripe.Customer.create(email=user.email)
        # ToDo (pduran): Should this go here????
        user.payment_service_user_id = customer.id
        await user_repo.update(user_id=user.id, user_update=user)
    else:
        customer = stripe.Customer.retrieve(id=user.payment_service_user_id)
    return customer.id

async def create_subscription(
    user: UserDomain,
    plan: PlanDomain,
    user_repo: UserRepository,
) -> str:
    customer_id = await get_or_create_user_id(user, user_repo)

    # Create a subscription for the user
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{'plan': plan_id}],
        expand=['latest_invoice.payment_intent'],
    )

    # Update user's subscription ID
    user.payment_service_subscription_id = subscription.id
    await user_repo.update(user_id=user.id, user_update=user)

    return subscription.id




