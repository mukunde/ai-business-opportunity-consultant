"""HTTP routes for the recommendation engine (Phase 1, Epic 5)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.recommendation import service
from app.schemas.recommendation import RecommendationRead
from app.scoring import service as scoring_service

router = APIRouter(prefix="/opportunities", tags=["recommendation"])


@router.post(
    "/{opportunity_id}/recommendation",
    response_model=RecommendationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_recommendation(
    opportunity_id: uuid.UUID, db: Session = Depends(get_db)
) -> RecommendationRead:
    """Decide from the latest score snapshot (status -> RECOMMENDED)."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    score = scoring_service.latest_score(db, opportunity_id)
    if score is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "No score to decide on yet; score first")
    recommendation = service.create_recommendation(db, opportunity, score)
    return RecommendationRead.model_validate(recommendation)


@router.get("/{opportunity_id}/recommendation", response_model=RecommendationRead)
def get_recommendation(
    opportunity_id: uuid.UUID, db: Session = Depends(get_db)
) -> RecommendationRead:
    """Return the latest recommendation for an opportunity."""
    recommendation = service.latest_recommendation(db, opportunity_id)
    if recommendation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No recommendation yet")
    return RecommendationRead.model_validate(recommendation)
