"""Dashboard aggregation: opportunities enriched with their latest signals.

Each opportunity's latest score, recommendation and completeness are read through
the existing per-opportunity service helpers. That is one small set of queries per
row (N+1) which is fine at the opportunity counts this tool handles; a window-
function rollup is the optimisation if the corpus ever grows.
"""

from sqlalchemy.orm import Session

from app import crud
from app.recommendation import service as recommendation_service
from app.schemas.opportunity import OpportunitySummaryRead
from app.scoring import service as scoring_service


def opportunity_summaries(
    db: Session, *, skip: int = 0, limit: int = 50
) -> list[OpportunitySummaryRead]:
    """List opportunities (newest first) with their latest score and recommendation."""
    summaries: list[OpportunitySummaryRead] = []
    for opp in crud.opportunity.list_opportunities(db, skip=skip, limit=limit):
        score = scoring_service.latest_score(db, opp.id)
        recommendation = recommendation_service.latest_recommendation(db, opp.id)
        completeness = scoring_service.latest_completeness(db, opp.id)
        summaries.append(
            OpportunitySummaryRead(
                id=opp.id,
                title=opp.title,
                business_area=opp.business_area,
                status=opp.status,
                current_version=opp.current_version,
                created_at=opp.created_at,
                final_score=score.final_score if score else None,
                confidence=score.confidence if score else None,
                completeness=completeness.overall_score if completeness else None,
                recommendation_type=recommendation.type.value if recommendation else None,
            )
        )
    return summaries
