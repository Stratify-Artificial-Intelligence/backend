from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    """Load Postgres connection settings from environment or .env."""

    DATABASE_URL: str = ''
