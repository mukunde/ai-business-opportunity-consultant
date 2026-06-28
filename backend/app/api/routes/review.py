"""HTTP routes for the human review decision (Phase 2, Epic 8 - ADR 0006)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.recommendation import service as recommendation_service
from app.review import service
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(prefix="/opportunities", tags=["review"])


@router.post(
    "/{opportunity_id}/review",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    opportunity_id: uuid.UUID,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
) -> ReviewRead:
    """Record a human approve/reject verdict (status -> APPROVED/REJECTED)."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    if recommendation_service.latest_recommendation(db, opportunity_id) is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No recommendation to review yet; recommend first",
        )
    review = service.create_review(db, opportunity, payload.decision, payload.note)
    return ReviewRead.model_validate(review)


@router.get("/{opportunity_id}/review", response_model=ReviewRead)
def get_review(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> ReviewRead:
    """Return the latest review for an opportunity."""
    review = service.latest_review(db, opportunity_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No review yet")
    return ReviewRead.model_validate(review)
