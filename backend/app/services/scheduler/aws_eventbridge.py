from boto3 import client

from app.services.scheduler import SchedulerProvider
from app.settings import GeneralSettings, SchedulerAWSEventBridgeSettings


general_settings = GeneralSettings()
settings = SchedulerAWSEventBridgeSettings()


class SchedulerAWSEventBridge(SchedulerProvider):
    """AWS EventBridge scheduler provider implementation."""

    def __init__(self):
        super().__init__()
        self.scheduler_client = client(
            'scheduler',
            region_name=settings.REGION,
            aws_access_key_id=settings.ACCESS_KEY_ID,
            aws_secret_access_key=settings.SECRET_ACCESS_KEY,
        )

    async def create_schedule(
        self,
        name: str,
        expression: str,
        target_endpoint: str,
        body: str,
    ) -> None:
        """Create a schedule in AWS EventBridge.

        This schedule will request to some of this Backend's endpoint, using the service
        user token for authentication.
        ToDo (pduran): Make this schedule more generic.
        """
        self.scheduler_client.create_schedule(
            Name=name,
            ScheduleExpression=expression,
            FlexibleTimeWindow={'Mode': 'OFF'},
            Target={
                'Arn': 'arn:aws:scheduler:::http-target',
                'RoleArn': settings.ROLE_ARN,
                'Endpoint': f'{general_settings.APP_DOMAIN}/{target_endpoint}',
                'RetryPolicy': {'MaximumRetryAttempts': 3},
                'HttpParameters': {
                    'HeaderParameters': {
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {general_settings.SERVICE_USER_TOKEN}',
                    },
                    'PathParameterValues': [],
                    'QueryStringParameters': {},
                    'Body': body,
                },
            },
            TargetType='Http',
            ActionAfterCompletion='DELETE',
        )
