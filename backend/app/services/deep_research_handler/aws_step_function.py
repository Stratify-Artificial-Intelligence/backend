import json

from boto3 import client

from app.services.deep_research_handler import DeepResearchHandlerProvider
from app.settings import DeepResearchHandlerAWSStepFunctionSettings


settings = DeepResearchHandlerAWSStepFunctionSettings()


class DeepResearchHandlerAWSStepFunction(DeepResearchHandlerProvider):
    """Implementation of DeepResearchHandlerProvider using AWS Step Function."""

    def __init__(self):
        self.step_function_client = client(
            'stepfunctions',
            region_name=settings.REGION,
            aws_access_key_id=settings.ACCESS_KEY_ID,
            aws_secret_access_key=settings.SECRET_ACCESS_KEY,
        )

    def track_and_store_research(self, research_id: str, business_id: int) -> None:
        try:
            self.step_function_client.start_execution(
                stateMachineArn=settings.STATE_MACHINE_ARN,
                input=json.dumps(
                    {
                        'research_id': research_id,
                        'business_id': business_id,
                    }
                ),
            )
        except Exception as e:
            raise RuntimeError(
                f'Failed to start Step Function execution for research {research_id} '
                f'and business {business_id}: {e}'
            )
