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

    # LLM (Anthropic Claude). The key is read from the environment; never commit
    # it. The interview engine uses Claude for context extraction and questioning.
    # Set LLM_PROVIDER=fake to run the whole flow offline with a deterministic
    # stub (no API key, no cost) - useful before wiring real billing.
    llm_provider: str = "claude"  # "claude" | "fake"
    anthropic_api_key: str | None = None
    llm_model: str = "claude-opus-4-8"

    # Interview engine. The loop keeps asking until context completeness reaches
    # this threshold, then hands off to structuring (TRD section 4.3).
    context_completeness_threshold: float = 1.0


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (one read per process)."""
    return Settings()
