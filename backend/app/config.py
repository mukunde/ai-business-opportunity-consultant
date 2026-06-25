"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration.

    Values are read from the process environment, falling back to a local
    ``.env`` file during development. See ``.env.example`` for the contract.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    app_name: str = "AI Business Opportunity Consultant"
    environment: str = "development"
    debug: bool = True

    # Database. Default points at the docker-compose Postgres service.
    database_url: str = "postgresql+psycopg://aiboc:aiboc@localhost:5432/aiboc"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (one read per process)."""
    return Settings()
