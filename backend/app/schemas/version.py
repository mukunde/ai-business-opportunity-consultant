"""Pydantic schemas for opportunity versioning."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VersionCreate(BaseModel):
    """Optional label when cutting a new version."""

    note: str | None = None


class SnapshotFact(BaseModel):
    label: str
    value: str


class AssessmentSnapshot(BaseModel):
    """The decision state captured in a version, mirroring the report inputs."""

    title: str
    problem_statement: str | None = None
    summary: str | None = None
    facts: list[SnapshotFact] = []
    assumptions: list[str] = []
    unknowns: list[str] = []
    completeness: dict[str, float] | None = None
    score: dict[str, float] | None = None
    recommendation_type: str | None = None
    recommendation_rationale: str | None = None


class VersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version_number: int
    note: str | None
    snapshot: AssessmentSnapshot
    created_at: datetime
