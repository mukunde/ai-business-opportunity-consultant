"""Reporting orchestration: gather persisted data, render Markdown, persist."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.context import (
    ContextCompleteness,
    ContextNode,
    ContextNodeType,
)
from app.models.interview import InterviewSession
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.recommendation import Recommendation
from app.models.reporting import DetailedAssessment, ExecutiveSummary
from app.models.scoring import ScoreSnapshot
from app.reporting.generator import (
    ReportData,
    build_detailed_assessment,
    build_executive_summary,
)


def _latest(db: Session, model: Any, opportunity_id: uuid.UUID, order_col: Any) -> Any:
    stmt = select(model).where(model.opportunity_id == opportunity_id).order_by(order_col.desc())
    return db.execute(stmt).scalars().first()


def gather_report_data(db: Session, opportunity: Opportunity) -> ReportData:
    """Assemble report inputs from the persisted entities."""
    session = _latest(db, InterviewSession, opportunity.id, InterviewSession.started_at)
    state = session.working_state if session else {}

    nodes = list(
        db.execute(
            select(ContextNode).where(ContextNode.opportunity_id == opportunity.id)
        ).scalars()
    )
    facts = [(n.label, n.description or "") for n in nodes if n.type == ContextNodeType.FACT]
    assumptions = [n.label for n in nodes if n.type == ContextNodeType.ASSUMPTION]
    unknowns = [n.label for n in nodes if n.type == ContextNodeType.UNKNOWN]

    completeness = _latest(db, ContextCompleteness, opportunity.id, ContextCompleteness.created_at)
    score = _latest(db, ScoreSnapshot, opportunity.id, ScoreSnapshot.created_at)
    recommendation = _latest(db, Recommendation, opportunity.id, Recommendation.created_at)

    return ReportData(
        title=opportunity.title,
        problem_statement=state.get("problem_statement"),
        summary=state.get("summary"),
        facts=facts,
        assumptions=assumptions,
        unknowns=unknowns,
        completeness=(
            {
                "business_context_score": completeness.business_context_score,
                "process_understanding_score": completeness.process_understanding_score,
                "data_readiness_score": completeness.data_readiness_score,
                "roi_readiness_score": completeness.roi_readiness_score,
                "overall_score": completeness.overall_score,
            }
            if completeness
            else None
        ),
        score=(
            {
                "roi_score": score.roi_score,
                "impact_score": score.impact_score,
                "feasibility_score": score.feasibility_score,
                "risk_score": score.risk_score,
                "strategic_alignment_score": score.strategic_alignment_score,
                "time_to_value_score": score.time_to_value_score,
                "final_score": score.final_score,
                "confidence": score.confidence,
            }
            if score
            else None
        ),
        recommendation_type=recommendation.type.value if recommendation else None,
        recommendation_rationale=(recommendation.rationale if recommendation else None),
    )


def generate_reports(
    db: Session, opportunity: Opportunity
) -> tuple[ExecutiveSummary, DetailedAssessment]:
    """Render and persist both reports, advancing the opportunity to REVIEW."""
    data = gather_report_data(db, opportunity)

    summary = ExecutiveSummary(
        opportunity_id=opportunity.id,
        markdown_content=build_executive_summary(data),
    )
    assessment = DetailedAssessment(
        opportunity_id=opportunity.id,
        markdown_content=build_detailed_assessment(data),
    )
    db.add(summary)
    db.add(assessment)
    opportunity.status = OpportunityStatus.REVIEW
    db.commit()
    db.refresh(summary)
    db.refresh(assessment)
    return summary, assessment


def latest_reports(
    db: Session, opportunity_id: uuid.UUID
) -> tuple[ExecutiveSummary | None, DetailedAssessment | None]:
    """Return the most recent executive summary and detailed assessment."""
    summary = _latest(db, ExecutiveSummary, opportunity_id, ExecutiveSummary.generated_at)
    assessment = _latest(db, DetailedAssessment, opportunity_id, DetailedAssessment.generated_at)
    return summary, assessment
