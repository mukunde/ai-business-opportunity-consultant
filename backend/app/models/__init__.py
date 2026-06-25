"""ORM models. Import models here so Alembic autogenerate sees them."""

from app.models.interview import (
    ConversationTurn,
    InterviewSession,
    InterviewStatus,
    TurnRole,
)
from app.models.opportunity import Opportunity, OpportunityStatus

__all__ = [
    "Opportunity",
    "OpportunityStatus",
    "InterviewSession",
    "InterviewStatus",
    "ConversationTurn",
    "TurnRole",
]
