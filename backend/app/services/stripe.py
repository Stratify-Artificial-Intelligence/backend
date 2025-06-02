import stripe

from app.settings import StripeSettings


settings = StripeSettings()
stripe.api_key = settings.API_KEY


async def get_customer(
    customer_id: str,
) -> stripe.Customer:
    return stripe.Customer.retrieve(id=customer_id)


async def create_customer(
    email: str,
) -> stripe.Customer:
    return stripe.Customer.create(
        email=email,
        description='Created from the Backend application',
    )


async def create_subscription(
    customer_id: str,
    plan_id: int,
) -> stripe.Subscription:
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{'price': 'price_1RVGp2Ive8AXNk92AY707LgP'}],
        expand=['latest_invoice.payment_intent'],
    )


async def create_client_intent(customer_id: str) -> stripe.SetupIntent:
    return stripe.SetupIntent.create(customer=customer_id)


async def setup_client_intent(customer_id: str, payment_method_id: str) -> None:
    stripe.PaymentMethod.attach(
        customer=customer_id,
        payment_method=payment_method_id,
    )


async def cancel_subscription(subscription_id) -> None:
    stripe.Subscription.delete(subscription_id)
