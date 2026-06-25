"""API package: aggregates all route routers under a single api_router."""

from fastapi import APIRouter

from app.api.routes import opportunities

api_router = APIRouter()
api_router.include_router(opportunities.router)

__all__ = ["api_router"]
