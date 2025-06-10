import stripe

from app.settings import StripeSettings


settings = StripeSettings()
stripe.api_key = settings.API_KEY


async def get_checkout_session(
    session_id: str,
) -> stripe.checkout.Session | None:
    """Retrieve a Stripe checkout session by its ID."""
    try:
        return stripe.checkout.Session.retrieve(id=session_id)
    except Exception:
        # Checkout session not found
        return None


async def create_checkout_session(
    success_url: str,
    cancel_url: str,
    price_id: str,
) -> stripe.checkout.Session:
    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='subscription',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )


async def get_subscription(subscription_id: str) -> stripe.Subscription:
    return stripe.Subscription.retrieve(id=subscription_id)


async def get_portal_session(
    customer_id: str,
    return_url: str,
) -> stripe.billing_portal.Session:
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )


async def verify_webhook_signature(payload: bytes, sig_header: str) -> stripe.Event:
    """Verify the Stripe webhook signature and return event."""
    try:
        return stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.WEBHOOK_SECRET,
        )
    except Exception as e:
        raise ValueError(f'Webhook verification failed: {e}') from e


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
    price_id: str,
) -> stripe.Subscription:
    return stripe.Subscription.create(
        customer=customer_id,
        items=[{'price': price_id}],
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
