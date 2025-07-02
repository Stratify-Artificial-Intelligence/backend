from enum import Enum


class ChatAIModelProviderEnum(str, Enum):
    OPENAI = 'openai'


class StorageProviderEnum(str, Enum):
    AWS_S3 = 'aws_s3'
