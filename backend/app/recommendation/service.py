"""Recommendation orchestration: decide from a score snapshot and persist it."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.recommendation import Recommendation
from app.models.scoring import ScoreSnapshot
from app.recommendation.engine import recommend


def latest_recommendation(db: Session, opportunity_id: uuid.UUID) -> Recommendation | None:
    """Most recent recommendation for an opportunity."""
    stmt = (
        select(Recommendation)
        .where(Recommendation.opportunity_id == opportunity_id)
        .order_by(Recommendation.created_at.desc())
    )
    return db.execute(stmt).scalars().first()


def create_recommendation(
    db: Session, opportunity: Opportunity, score: ScoreSnapshot
) -> Recommendation:
    """Decide from a score snapshot and persist, advancing to RECOMMENDED."""
    rec_type, rationale = recommend(
        final_score=score.final_score,
        confidence=score.confidence,
        risk_score=score.risk_score,
        feasibility_score=score.feasibility_score,
    )
    recommendation = Recommendation(
        opportunity_id=opportunity.id,
        score_snapshot_id=score.id,
        type=rec_type,
        rationale=rationale,
        confidence=score.confidence,
    )
    db.add(recommendation)
    opportunity.status = OpportunityStatus.RECOMMENDED
    db.commit()
    db.refresh(recommendation)
    return recommendation
