"""HTTP routes for the scoring engine (Phase 1, Epic 4)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.schemas.scoring import ScoreInput, ScoreRead
from app.scoring import service

router = APIRouter(prefix="/opportunities", tags=["scoring"])


@router.post(
    "/{opportunity_id}/score",
    response_model=ScoreRead,
    status_code=status.HTTP_201_CREATED,
)
def create_score(
    opportunity_id: uuid.UUID,
    payload: ScoreInput,
    db: Session = Depends(get_db),
) -> ScoreRead:
    """Score an opportunity. Confidence reflects context completeness."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    completeness = service.latest_completeness(db, opportunity_id)
    if completeness is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No context to score yet; run an interview first",
        )
    snapshot = service.create_score(
        db,
        opportunity,
        completeness,
        impact=payload.impact,
        ease=payload.ease,
        strategic_alignment=payload.strategic_alignment,
    )
    return ScoreRead.model_validate(snapshot)


@router.get("/{opportunity_id}/score", response_model=ScoreRead)
def get_score(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> ScoreRead:
    """Return the latest score snapshot for an opportunity."""
    snapshot = service.latest_score(db, opportunity_id)
    if snapshot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No score yet")
    return ScoreRead.model_validate(snapshot)
