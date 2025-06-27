from typing import BinaryIO

from boto3 import client

from app.settings import AWSStorageSettings


settings = AWSStorageSettings()
s3_client = client(
    's3',
    region_name=settings.REGION,
    aws_access_key_id=settings.ACCESS_KEY_ID,
    aws_secret_access_key=settings.SECRET_ACCESS_KEY,
)


async def upload_file_to_s3(
    file_binary: BinaryIO,
    file_name: str,
    file_content_type: str,
) -> str:
    """Upload a file to an S3 bucket and return its URL."""
    s3_client.upload_fileobj(
        Fileobj=file_binary,
        Bucket=settings.BUCKET_NAME,
        Key=file_name,
        ExtraArgs={'ContentType': file_content_type},
    )
    return (
        f'https://{settings.BUCKET_NAME}.s3.{settings.REGION}.amazonaws.com/{file_name}'
    )


async def remove_file_from_s3(file_name: str) -> None:
    """Remove a file from an S3 bucket."""
    s3_client.delete_object(
        Bucket=settings.BUCKET_NAME,
        Key=file_name,
    )
