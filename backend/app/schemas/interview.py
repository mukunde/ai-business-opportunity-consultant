"""Pydantic schemas for the interview API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.interview import InterviewStatus, TurnRole


class InterviewStartRequest(BaseModel):
    """Kick off an interview with the user's raw idea/description."""

    message: str = Field(..., min_length=1)


class ContinueRequest(BaseModel):
    """One user answer to the consultant's last question."""

    answer: str = Field(..., min_length=1)


class TurnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: TurnRole
    message: str
    reasoning_trace: str | None
    created_at: datetime


class ContextView(BaseModel):
    """The live context model the consultant has built (UX right panel)."""

    context: dict[str, str]
    missing: list[str]
    assumptions: list[str]
    completeness: float


class InterviewTurnResponse(BaseModel):
    """Returned after start/continue: the consultant's next move."""

    session_id: uuid.UUID
    status: InterviewStatus
    assistant_message: str
    done: bool
    context: ContextView


class InterviewSessionRead(BaseModel):
    """Full session view with transcript (GET)."""

    session_id: uuid.UUID
    opportunity_id: uuid.UUID
    status: InterviewStatus
    context: ContextView
    turns: list[TurnRead]
