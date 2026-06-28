"""Pydantic schemas for the reporting API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.reporting import DeliverableKind


class ReportDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    markdown_content: str
    generated_at: datetime


class ReportBundle(BaseModel):
    """Both decision-ready documents for an opportunity."""

    executive_summary: ReportDocumentRead
    detailed_assessment: ReportDocumentRead


class DeliverableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: DeliverableKind
    markdown_content: str
    generated_at: datetime
