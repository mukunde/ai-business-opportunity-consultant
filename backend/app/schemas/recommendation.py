"""Pydantic schemas for the recommendation API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.recommendation import RecommendationType


class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    opportunity_id: uuid.UUID
    score_snapshot_id: uuid.UUID
    type: RecommendationType
    rationale: str
    confidence: float
    created_at: datetime
