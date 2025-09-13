from .base import BackendError


class SubscriptionWebhookBusinessError(BackendError):
    def __init__(self, user_id: int, business_id: int, error: Exception):
        super().__init__()
        self.user_id = user_id
        self.business_id = business_id
        self.error = error

    def __str__(self):
        return (
            f'SubscriptionWebhookBusinessError for user {self.user_id} and business '
            f'{self.business_id}: {self.error}'
        )


class SubscriptionWebhookErrors(BackendError):
    def __init__(self, user_id: int, errors: list[SubscriptionWebhookBusinessError]):
        super().__init__()
        self.user_id = user_id
        self.errors = errors

    def __str__(self):
        return (
            f'SubscriptionWebhookErrors for user {self.user_id} with {len(self.errors)} '
            f"errors: {','.join(str(e) for e in self.errors)}"
        )
