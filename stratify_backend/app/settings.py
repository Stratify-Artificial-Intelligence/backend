from pydantic_settings import BaseSettings, SettingsConfigDict


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
