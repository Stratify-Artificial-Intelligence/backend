import stripe

from app.settings import StripeSettings


# ToDo (pduran): Refactor this into the ServiceFactory


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
    customer_id: str,
) -> stripe.checkout.Session:
    return stripe.checkout.Session.create(
        customer=customer_id,
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


async def create_customer(email: str, name: str | None = None) -> stripe.Customer:
    return stripe.Customer.create(
        email=email,
        name=name if name is not None else email,
        description='Created from the Backend application',
    )
