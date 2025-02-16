from pydantic_settings import BaseSettings


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

    class Config:
        env_file = '.env'
