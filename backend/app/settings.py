from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import (
    ChatAIModelProviderEnum,
    DeepResearchHandlerProviderEnum,
    DeepResearchProviderEnum,
    EmbeddingProviderEnum,
    IdentityProviderEnum,
    SchedulerProviderEnum,
    StorageProviderEnum,
    VectorDatabaseProviderEnum,
)


class GeneralSettings(BaseSettings):
    """General settings for the application."""

    SERVICE_USER_TOKEN: str = ''
    APP_DOMAIN: str = 'localhost'

    model_config = SettingsConfigDict(env_file='.env', env_prefix='SECURITY_')


class ServicesSettings(BaseSettings):
    """Load Services settings from environment or .env."""

    CHAT_AI_MODEL_PROVIDER: ChatAIModelProviderEnum = ChatAIModelProviderEnum.ANTHROPIC
    DEEP_RESEARCH_PROVIDER: DeepResearchProviderEnum = (
        DeepResearchProviderEnum.PERPLEXITY
    )
    DEEP_RESEARCH_HANDLER_PROVIDER: DeepResearchHandlerProviderEnum = (
        DeepResearchHandlerProviderEnum.AWS_STEP_FUNCTION
    )
    EMBEDDING_PROVIDER: EmbeddingProviderEnum = EmbeddingProviderEnum.OPENAI
    IDENTITY_PROVIDER: IdentityProviderEnum = IdentityProviderEnum.FIREBASE_AUTH
    SCHEDULER_PROVIDER: SchedulerProviderEnum = SchedulerProviderEnum.AWS_EVENTBRIDGE
    STORAGE_PROVIDER: StorageProviderEnum = StorageProviderEnum.AWS_S3
    VECTOR_DATABASE_PROVIDER: VectorDatabaseProviderEnum = (
        VectorDatabaseProviderEnum.PINECONE
    )

    model_config = SettingsConfigDict(env_file='.env', env_prefix='SERVICES_')


class PostgresSettings(BaseSettings):
    """Load Postgres connection settings from environment or .env."""

    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''
    POSTGRES_SERVER: str = ''
    POSTGRES_DB: str = ''

    @property
    def database_url(self) -> str:
        return (
            'postgresql+asyncpg://'
            f'{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}'
        )

    model_config = SettingsConfigDict(env_file='.env')


class FirebaseAuthSettings(BaseSettings):
    """Load Firebase Auth settings from environment or .env."""

    PRIVATE_KEY: dict = {}
    API_KEY: dict = {}

    model_config = SettingsConfigDict(env_file='.env', env_prefix='FIREBASE_AUTH_')


# ToDo (pduran): Rename class to StorageAWSS3Settings. Also rename env_prefix
class AWSStorageSettings(BaseSettings):
    """Load AWS S3 storage settings from environment or .env."""

    BUCKET_NAME: str = ''
    REGION: str = ''
    ACCESS_KEY_ID: str = ''
    SECRET_ACCESS_KEY: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='STORAGE_')


# ToDo (pduran): Rename class to ChatAIModelOpenAISettings. Also rename env_prefix
class OpenAISettings(BaseSettings):
    """Load Open AI settings from environment or .env."""

    API_KEY: str = ''
    ASSISTANT_ID: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='OPEN_AI_')


# ToDo (pduran): Rename class to ChatAIModelAnthropicSettings. Also rename env_prefix
class AnthropicSettings(BaseSettings):
    """Load Anthropic settings from environment or .env."""

    API_KEY: str = ''
    MODEL_NAME: str = 'claude-sonnet-4-20250514'
    MAX_TOKENS: int = 8192
    TEMPERATURE: float = 1

    model_config = SettingsConfigDict(env_file='.env', env_prefix='ANTHROPIC_')


class OpenAIEmbeddingSettings(BaseSettings):
    """Load Open AI Embedding settings from environment or .env."""

    API_KEY: str = ''
    MODEL_NAME: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='OPEN_AI_EMBEDDING_')


class PerplexitySettings(BaseSettings):
    """Load Perplexity settings from environment or .env."""

    API_URL: str = ''
    API_URL_ASYNC: str = ''
    API_KEY: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='PERPLEXITY_')


class PineconeSettings(BaseSettings):
    """Load Pinecone settings from environment or .env."""

    API_KEY: str = ''
    REGION: str = ''
    CLOUD: str = ''
    MESSAGE_LIMIT_BYTES: int = 2 * 1024 * 1024  # 2MB

    model_config = SettingsConfigDict(env_file='.env', env_prefix='PINECONE_')


class RAGSettings(BaseSettings):
    """Load RAG settings from environment or .env."""

    MAX_TOKENS: int = 600
    OVERLAP: int = 170
    VECTOR_ID: str = 'doc{doc_index}_chunk{chunk_index}'
    NAMESPACE_ID: str = 'business_{business_id}'
    INDEX_NAME: str = 'veyra-index'
    INDEX_DIMENSION: int = 1536
    INDEX_METRIC: str = 'cosine'
    TOP_K: int = 1

    model_config = SettingsConfigDict(env_file='.env', env_prefix='RAG_')


class GeneralRAGSettings(RAGSettings):
    """Load General RAG settings from environment or .env."""

    MAX_TOKENS: int = 400
    OVERLAP: int = 200
    NAMESPACE_ID: str = 'general'
    INDEX_NAME: str = 'veyra-general-index'
    TOP_K: int = 5

    model_config = SettingsConfigDict(env_file='.env', env_prefix='GENERAL_RAG_')


class DeepResearchHandlerAWSStepFunctionSettings(BaseSettings):
    """Load Deep Research Handler AWS Step Function settings from environment or .env."""

    REGION: str = ''
    STATE_MACHINE_ARN: str = ''
    ACCESS_KEY_ID: str = ''
    SECRET_ACCESS_KEY: str = ''

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='SERVICES_DEEP_RESEARCH_HANDLER_AWS_STEP_FUNCTION_',
    )


class SchedulerAWSEventBridgeSettings(BaseSettings):
    """Load Scheduler AWS Event Bridge settings from environment or .env."""

    REGION: str = ''
    ACCESS_KEY_ID: str = ''
    SECRET_ACCESS_KEY: str = ''
    ROLE_ARN: str = ''

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='SERVICES_SCHEDULER_AWS_EVENTBRIDGE_',
    )


class StripeSettings(BaseSettings):
    """Load Stripe settings from environment or .env."""

    API_KEY: str = ''
    WEBHOOK_SECRET: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='STRIPE_')
