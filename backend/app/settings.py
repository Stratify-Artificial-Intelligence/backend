import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import AuthMethodEnum


class SecuritySettings(BaseSettings):
    """General settings for the application."""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOKEN_ENCRYPTION_ALGORITHM: str = 'HS256'
    AUTH_METHOD: str = AuthMethodEnum.OAUTH2
    FIRST_SUPERUSER_USERNAME: str = 'admin'
    FIRST_BASIC_USER_USERNAME: str = 'user'

    model_config = SettingsConfigDict(env_file='.env')


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


class OpenAISettings(BaseSettings):
    """Load Open AI settings from environment or .env."""

    API_KEY: str = ''
    ASSISTANT_ID: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='OPEN_AI_')


class OpenAIEmbeddingSettings(BaseSettings):
    """Load Open AI Embedding settings from environment or .env."""

    API_KEY: str = ''
    MODEL_NAME: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='OPEN_AI_EMBEDDING_')


class PerplexitySettings(BaseSettings):
    """Load Perplexity settings from environment or .env."""

    API_URL: str = ''
    API_KEY: str = ''

    model_config = SettingsConfigDict(env_file='.env', env_prefix='PERPLEXITY_')


class PineconeSettings(BaseSettings):
    """Load Pinecone settings from environment or .env."""

    API_KEY: str = ''
    REGION: str = ''
    CLOUD: str = ''

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
    TOP_K: int = 8

    model_config = SettingsConfigDict(env_file='.env', env_prefix='RAG_')
