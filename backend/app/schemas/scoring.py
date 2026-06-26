"""Pydantic schemas for the scoring API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScoreInput(BaseModel):
    """Analyst-judged ICE-style inputs (1-10). Objective dimensions are derived
    from the context graph, so they are not provided here."""

    impact: int = Field(..., ge=1, le=10)
    ease: int = Field(..., ge=1, le=10)
    strategic_alignment: int = Field(..., ge=1, le=10)


class ScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    opportunity_id: uuid.UUID
    roi_score: float
    impact_score: float
    feasibility_score: float
    risk_score: float
    strategic_alignment_score: float
    time_to_value_score: float
    final_score: float
    confidence: float
    created_at: datetime
