from fastapi import UploadFile, HTTPException, status

from app.domain import Business as BusinessDomain
from app.services.aws_storage import remove_file_from_s3, upload_file_to_s3

from urllib.parse import urlparse


async def upload_business_image(file: UploadFile, business: BusinessDomain) -> str:
    if file.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid image format {file.content_type}. Use JPEG or PNG.',
        )
    file_name = _get_business_image_name(file=file, business=business)
    return await upload_file_to_s3(
        file_binary=file.file,
        file_name=file_name,
        file_content_type=file.content_type,
    )


async def remove_business_image(business: BusinessDomain) -> None:
    if business.logo_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Business idea does not have a logo to delete.',
        )
    parsed_url = urlparse(business.logo_url)
    file_name = parsed_url.path.lstrip('/')
    await remove_file_from_s3(file_name=file_name)


def _get_business_image_name(file: UploadFile, business: BusinessDomain) -> str:
    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File name is required.',
        )
    extension = file.filename.split('.')[-1]
    return f'business_logos/logo_{business.id}.{extension}'
