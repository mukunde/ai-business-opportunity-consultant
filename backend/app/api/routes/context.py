"""HTTP route exposing the persistent context graph (Phase 1, Epic 3)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.models.context import (
    ContextCompleteness,
    ContextNode,
    ContextRelationship,
    Contradiction,
    Evidence,
)
from app.schemas.context import (
    CompletenessRead,
    ContextGraphRead,
    ContradictionRead,
    EvidenceRead,
    NodeRead,
    RelationshipRead,
)

router = APIRouter(prefix="/opportunities", tags=["context"])


@router.get("/{opportunity_id}/context", response_model=ContextGraphRead)
def get_context(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> ContextGraphRead:
    """Return the full context graph the consultant has built so far."""
    if crud.opportunity.get_opportunity(db, opportunity_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")

    nodes = list(
        db.execute(
            select(ContextNode).where(ContextNode.opportunity_id == opportunity_id)
        ).scalars()
    )
    node_ids = [n.id for n in nodes]
    relationships = (
        list(
            db.execute(
                select(ContextRelationship).where(ContextRelationship.source_node_id.in_(node_ids))
            ).scalars()
        )
        if node_ids
        else []
    )
    evidence = list(
        db.execute(select(Evidence).where(Evidence.opportunity_id == opportunity_id)).scalars()
    )
    contradictions = list(
        db.execute(
            select(Contradiction).where(Contradiction.opportunity_id == opportunity_id)
        ).scalars()
    )
    completeness = (
        db.execute(
            select(ContextCompleteness)
            .where(ContextCompleteness.opportunity_id == opportunity_id)
            .order_by(ContextCompleteness.created_at.desc())
        )
        .scalars()
        .first()
    )

    return ContextGraphRead(
        nodes=[NodeRead.model_validate(n) for n in nodes],
        relationships=[RelationshipRead.model_validate(r) for r in relationships],
        evidence=[EvidenceRead.model_validate(e) for e in evidence],
        contradictions=[ContradictionRead.model_validate(c) for c in contradictions],
        completeness=(CompletenessRead.model_validate(completeness) if completeness else None),
    )
