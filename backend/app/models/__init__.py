"""ORM models. Import models here so Alembic autogenerate sees them."""

from app.models.context import (
    ContextCompleteness,
    ContextNode,
    ContextNodeType,
    ContextRelationship,
    Contradiction,
    ContradictionStatus,
    Evidence,
    EvidenceType,
    RelationType,
)
from app.models.interview import (
    ConversationTurn,
    InterviewSession,
    InterviewStatus,
    TurnRole,
)
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.recommendation import Recommendation, RecommendationType
from app.models.scoring import ScoreSnapshot

__all__ = [
    "Opportunity",
    "OpportunityStatus",
    "ScoreSnapshot",
    "Recommendation",
    "RecommendationType",
    "InterviewSession",
    "InterviewStatus",
    "ConversationTurn",
    "TurnRole",
    "ContextNode",
    "ContextNodeType",
    "ContextRelationship",
    "RelationType",
    "Evidence",
    "EvidenceType",
    "Contradiction",
    "ContradictionStatus",
    "ContextCompleteness",
]
