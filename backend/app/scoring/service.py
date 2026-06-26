"""Scoring orchestration: read context completeness, score, persist a snapshot."""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.context import ContextCompleteness
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.scoring import ScoreSnapshot
from app.scoring.engine import compute_scores


def latest_completeness(db: Session, opportunity_id: uuid.UUID) -> ContextCompleteness | None:
    """Most recent completeness snapshot for an opportunity (None if no interview)."""
    stmt = (
        select(ContextCompleteness)
        .where(ContextCompleteness.opportunity_id == opportunity_id)
        .order_by(ContextCompleteness.created_at.desc())
    )
    return db.execute(stmt).scalars().first()


def latest_score(db: Session, opportunity_id: uuid.UUID) -> ScoreSnapshot | None:
    """Most recent score snapshot for an opportunity."""
    stmt = (
        select(ScoreSnapshot)
        .where(ScoreSnapshot.opportunity_id == opportunity_id)
        .order_by(ScoreSnapshot.created_at.desc())
    )
    return db.execute(stmt).scalars().first()


def create_score(
    db: Session,
    opportunity: Opportunity,
    completeness: ContextCompleteness,
    impact: int,
    ease: int,
    strategic_alignment: int,
) -> ScoreSnapshot:
    """Compute and persist a score snapshot, advancing the opportunity to SCORING."""
    scores = compute_scores(
        {
            "overall_score": completeness.overall_score,
            "data_readiness_score": completeness.data_readiness_score,
            "roi_readiness_score": completeness.roi_readiness_score,
        },
        impact=impact,
        ease=ease,
        strategic_alignment=strategic_alignment,
    )
    snapshot = ScoreSnapshot(opportunity_id=opportunity.id, **scores)
    db.add(snapshot)
    opportunity.status = OpportunityStatus.SCORING
    db.commit()
    db.refresh(snapshot)
    return snapshot
