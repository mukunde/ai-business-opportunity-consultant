"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api import api_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
    )

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        """Liveness probe."""
        return {"status": "ok"}

    app.include_router(api_router)
    return app


app = create_app()
