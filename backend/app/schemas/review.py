"""Pydantic schemas for the review API (Epic 8, ADR 0006)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.review import ReviewDecision


class ReviewCreate(BaseModel):
    decision: ReviewDecision
    note: str | None = None


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    decision: ReviewDecision
    note: str | None
    created_at: datetime
