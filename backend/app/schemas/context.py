"""Pydantic schemas for the context graph API."""

import uuid

from pydantic import BaseModel, ConfigDict

from app.models.context import (
    ContextNodeType,
    ContradictionStatus,
    EvidenceType,
    RelationType,
)


class NodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: ContextNodeType
    label: str
    description: str | None
    confidence: float
    source_id: uuid.UUID | None


class RelationshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    relation_type: RelationType


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: EvidenceType
    content: str
    confidence: float


class ContradictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    node_a_id: uuid.UUID | None
    node_b_id: uuid.UUID | None
    status: ContradictionStatus
    resolution_note: str | None


class CompletenessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    business_context_score: float
    process_understanding_score: float
    data_readiness_score: float
    roi_readiness_score: float
    overall_score: float


class ContextGraphRead(BaseModel):
    """The full context graph for an opportunity (UX left + right panels)."""

    nodes: list[NodeRead]
    relationships: list[RelationshipRead]
    evidence: list[EvidenceRead]
    contradictions: list[ContradictionRead]
    completeness: CompletenessRead | None
