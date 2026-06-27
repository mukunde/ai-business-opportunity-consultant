"""Pydantic schemas: the API contract for Opportunity resources."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.opportunity import OpportunityStatus


class OpportunityCreate(BaseModel):
    """Payload to create an opportunity (Flow 1 - Create New Opportunity)."""

    title: str = Field(..., min_length=1, max_length=255)
    business_area: str | None = Field(default=None, max_length=255)
    owner_id: uuid.UUID | None = None


class OpportunityUpdate(BaseModel):
    """Partial update. Every field is optional; unset fields are untouched."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    business_area: str | None = Field(default=None, max_length=255)
    status: OpportunityStatus | None = None
    owner_id: uuid.UUID | None = None


class OpportunityRead(BaseModel):
    """Opportunity as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    business_area: str | None
    status: OpportunityStatus
    current_version: int
    owner_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class OpportunitySummaryRead(BaseModel):
    """An opportunity plus its latest score/recommendation, for the dashboard."""

    id: uuid.UUID
    title: str
    business_area: str | None
    status: OpportunityStatus
    current_version: int
    created_at: datetime
    final_score: float | None = None
    confidence: float | None = None
    completeness: float | None = None
    recommendation_type: str | None = None
    # Quadrant axes for the portfolio matrix (Impact x Feasibility).
    impact_score: float | None = None
    feasibility_score: float | None = None
