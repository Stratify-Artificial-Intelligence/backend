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
