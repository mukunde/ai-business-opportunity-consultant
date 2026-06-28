"""Pydantic schemas for the Discovery API (ADR 0004)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.discovery import DiscoveryStatus


class DiscoveryStart(BaseModel):
    title: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)  # initial free-text business description


class DiscoveryAnswer(BaseModel):
    answer: str = Field(..., min_length=1)


class SignalIngest(BaseModel):
    """A signal pushed into the session without an interview (ingestion seam)."""

    label: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class DiscoveryTurnRead(BaseModel):
    role: str
    message: str


class DiscoverySessionRead(BaseModel):
    id: uuid.UUID
    title: str
    status: DiscoveryStatus
    completeness: float
    next_question: str | None
    done: bool
    context: dict[str, str]
    pain_points: list[str]
    signals: list[dict[str, str]]
    turns: list[DiscoveryTurnRead]


class DiscoverySessionSummary(BaseModel):
    """A discovery session as listed on the discovery landing page."""

    id: uuid.UUID
    title: str
    status: DiscoveryStatus
    completeness: float
    done: bool
    created_at: datetime


class DiscoveredOpportunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    target_pain_point: str
    rationale: str
    promoted_opportunity_id: uuid.UUID | None
