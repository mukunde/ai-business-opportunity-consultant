"""Versioning orchestration: snapshot the current assessment, list history.

A version reuses the reporting layer's ``gather_report_data`` to assemble the
current decision state, so a version and a report always tell the same story.
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.version import OpportunityVersion
from app.reporting.service import gather_report_data
from app.schemas.version import AssessmentSnapshot, SnapshotFact


def _snapshot(db: Session, opportunity: Opportunity) -> AssessmentSnapshot:
    data = gather_report_data(db, opportunity)
    return AssessmentSnapshot(
        title=data.title,
        problem_statement=data.problem_statement,
        summary=data.summary,
        facts=[SnapshotFact(label=label, value=value) for label, value in data.facts],
        assumptions=data.assumptions,
        unknowns=data.unknowns,
        completeness=data.completeness,
        score=data.score,
        recommendation_type=data.recommendation_type,
        recommendation_rationale=data.recommendation_rationale,
    )


def create_version(
    db: Session, opportunity: Opportunity, note: str | None = None
) -> OpportunityVersion:
    """Freeze the current assessment as the next numbered version."""
    highest = db.execute(
        select(func.max(OpportunityVersion.version_number)).where(
            OpportunityVersion.opportunity_id == opportunity.id
        )
    ).scalar()
    next_number = (highest or 0) + 1

    version = OpportunityVersion(
        opportunity_id=opportunity.id,
        version_number=next_number,
        note=note,
        snapshot=_snapshot(db, opportunity).model_dump(),
    )
    db.add(version)
    opportunity.current_version = next_number
    db.commit()
    db.refresh(version)
    return version


def list_versions(db: Session, opportunity_id: uuid.UUID) -> list[OpportunityVersion]:
    """Return an opportunity's versions, newest first."""
    stmt = (
        select(OpportunityVersion)
        .where(OpportunityVersion.opportunity_id == opportunity_id)
        .order_by(OpportunityVersion.version_number.desc())
    )
    return list(db.execute(stmt).scalars())


def get_version(
    db: Session, opportunity_id: uuid.UUID, version_id: uuid.UUID
) -> OpportunityVersion | None:
    """Return one version scoped to its opportunity."""
    stmt = select(OpportunityVersion).where(
        OpportunityVersion.id == version_id,
        OpportunityVersion.opportunity_id == opportunity_id,
    )
    return db.execute(stmt).scalars().first()
