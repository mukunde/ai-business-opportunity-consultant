"""API package: aggregates all route routers under a single api_router."""

from fastapi import APIRouter

from app.api.routes import (
    context,
    interview,
    opportunities,
    recommendation,
    reporting,
    scoring,
    versions,
)

api_router = APIRouter()
api_router.include_router(opportunities.router)
api_router.include_router(interview.router)
api_router.include_router(context.router)
api_router.include_router(scoring.router)
api_router.include_router(recommendation.router)
api_router.include_router(reporting.router)
api_router.include_router(versions.router)

__all__ = ["api_router"]
