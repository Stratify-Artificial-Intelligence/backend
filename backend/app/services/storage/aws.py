from typing import BinaryIO

from boto3 import client

from app.services.storage import StorageProvider
from app.settings import AWSStorageSettings


settings = AWSStorageSettings()


class StorageAWSS3(StorageProvider):
    """AWS S3 storage provider implementation."""

    def __init__(self):
        super().__init__()
        self.s3_client = client(
            's3',
            region_name=settings.REGION,
            aws_access_key_id=settings.ACCESS_KEY_ID,
            aws_secret_access_key=settings.SECRET_ACCESS_KEY,
        )

    async def upload_file(
        self,
        file_binary: BinaryIO,
        file_name: str,
        file_content_type: str,
    ) -> str:
        self.s3_client.upload_fileobj(
            Fileobj=file_binary,
            Bucket=settings.BUCKET_NAME,
            Key=file_name,
            ExtraArgs={'ContentType': file_content_type},
        )
        return f'https://{settings.BUCKET_NAME}.s3.{settings.REGION}.amazonaws.com/{file_name}'  # noqa: E501

    async def remove_file(self, file_name: str) -> None:
        self.s3_client.delete_object(
            Bucket=settings.BUCKET_NAME,
            Key=file_name,
        )
