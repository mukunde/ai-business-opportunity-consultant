"""Review orchestration: record a human verdict and close the lifecycle (ADR 0006)."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.review import Review, ReviewDecision

_FINAL_STATUS = {
    ReviewDecision.APPROVE: OpportunityStatus.APPROVED,
    ReviewDecision.REJECT: OpportunityStatus.REJECTED,
}


def create_review(
    db: Session, opportunity: Opportunity, decision: ReviewDecision, note: str | None
) -> Review:
    """Record an append-only verdict and move the opportunity to its final state."""
    review = Review(opportunity_id=opportunity.id, decision=decision, note=note)
    db.add(review)
    opportunity.status = _FINAL_STATUS[decision]
    db.commit()
    db.refresh(review)
    return review


def latest_review(db: Session, opportunity_id: uuid.UUID) -> Review | None:
    """Most recent review for an opportunity."""
    stmt = (
        select(Review)
        .where(Review.opportunity_id == opportunity_id)
        .order_by(Review.created_at.desc())
    )
    return db.execute(stmt).scalars().first()
