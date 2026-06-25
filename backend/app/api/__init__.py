"""API package: aggregates all route routers under a single api_router."""

from fastapi import APIRouter

from app.api.routes import interview, opportunities

api_router = APIRouter()
api_router.include_router(opportunities.router)
api_router.include_router(interview.router)

__all__ = ["api_router"]
