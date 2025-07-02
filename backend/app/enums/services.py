from enum import Enum


class ChatAIModelProviderEnum(str, Enum):
    OPENAI = 'openai'


class EmbeddingProviderEnum(str, Enum):
    OPENAI = 'openai'


class IdentityProviderEnum(str, Enum):
    FIREBASE_AUTH = 'firebase_auth'


class StorageProviderEnum(str, Enum):
    AWS_S3 = 'aws_s3'
