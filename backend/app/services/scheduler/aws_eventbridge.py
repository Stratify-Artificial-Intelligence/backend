import json

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
        body: dict,
    ) -> None:
        """Create a schedule in AWS EventBridge.

        This schedule will trigger the lambda function that processes the task.
        ToDo (pduran): Make this schedule more generic.
        """
        try:
            self.scheduler_client.create_schedule(
                Name=name,
                GroupName=settings.GROUP_NAME,
                ScheduleExpression=expression,
                ScheduleExpressionTimezone='UTC',
                Target={
                    'Arn': settings.LAMBDA_FUNCTION_ARN,
                    'RoleArn': settings.ROLE_ARN,
                    'Input': json.dumps(body),
                },
                ActionAfterCompletion='DELETE',
                FlexibleTimeWindow={'Mode': 'OFF'},
            )
        except self.scheduler_client.exceptions.ConflictException:
            self.scheduler_client.update_schedule(
                Name=name,
                GroupName=settings.GROUP_NAME,
                ScheduleExpression=expression,
                ScheduleExpressionTimezone='UTC',
                Target={
                    'Arn': settings.LAMBDA_FUNCTION_ARN,
                    'RoleArn': settings.ROLE_ARN,
                    'Input': json.dumps(body),
                },
                FlexibleTimeWindow={'Mode': 'OFF'},
            )

    async def delete_schedule(
        self,
        name: str,
        group_name: str,
    ) -> None:
        """Delete a schedule in AWS EventBridge (if exists)."""
        try:
            self.scheduler_client.delete_schedule(
                Name=name,
                GroupName=group_name,
            )
        except self.scheduler_client.exceptions.ResourceNotFoundException:
            pass
