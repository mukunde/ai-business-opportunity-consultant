"""HTTP routes for reporting (Phase 1, Epic 6)."""

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.interview.llm import LLMClient, get_llm
from app.models.reporting import DeliverableKind
from app.recommendation import service as recommendation_service
from app.reporting import service
from app.reporting.pdf import render_report_pdf
from app.schemas.reporting import DeliverableRead, ReportBundle, ReportDocumentRead

router = APIRouter(prefix="/opportunities", tags=["reporting"])


def _pdf_filename(title: str) -> str:
    """Slugify the opportunity title into a safe download filename."""
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", title).strip("-").lower()
    return f"{slug or 'opportunity'}-report.pdf"


@router.post(
    "/{opportunity_id}/report",
    response_model=ReportBundle,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> ReportBundle:
    """Generate the executive summary and detailed assessment (status -> REVIEW)."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    if recommendation_service.latest_recommendation(db, opportunity_id) is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No recommendation to report on yet; recommend first",
        )
    summary, assessment = service.generate_reports(db, opportunity)
    return ReportBundle(
        executive_summary=ReportDocumentRead.model_validate(summary),
        detailed_assessment=ReportDocumentRead.model_validate(assessment),
    )


@router.get("/{opportunity_id}/report", response_model=ReportBundle)
def get_report(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> ReportBundle:
    """Return the latest generated reports for an opportunity."""
    summary, assessment = service.latest_reports(db, opportunity_id)
    if summary is None or assessment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No report generated yet")
    return ReportBundle(
        executive_summary=ReportDocumentRead.model_validate(summary),
        detailed_assessment=ReportDocumentRead.model_validate(assessment),
    )


@router.get(
    "/{opportunity_id}/report.pdf",
    response_class=Response,
    responses={200: {"content": {"application/pdf": {}}}},
)
def get_report_pdf(opportunity_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    """Return the latest reports rendered as a single downloadable PDF."""
    summary, assessment = service.latest_reports(db, opportunity_id)
    if summary is None or assessment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No report generated yet")
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    pdf_bytes = render_report_pdf(
        summary_md=summary.markdown_content,
        assessment_md=assessment.markdown_content,
    )
    filename = _pdf_filename(opportunity.title if opportunity else "opportunity")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{opportunity_id}/deliverables/{kind}",
    response_model=DeliverableRead,
    status_code=status.HTTP_201_CREATED,
)
def generate_deliverable(
    opportunity_id: uuid.UUID,
    kind: DeliverableKind,
    db: Session = Depends(get_db),
    llm: LLMClient = Depends(get_llm),
) -> DeliverableRead:
    """Generate one handoff deliverable for a validated opportunity (ADR 0005)."""
    opportunity = crud.opportunity.get_opportunity(db, opportunity_id)
    if opportunity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Opportunity not found")
    if recommendation_service.latest_recommendation(db, opportunity_id) is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "No recommendation yet; recommend before generating deliverables",
        )
    deliverable = service.generate_deliverable(db, opportunity, kind, llm)
    return DeliverableRead.model_validate(deliverable)


@router.get("/{opportunity_id}/deliverables", response_model=list[DeliverableRead])
def list_deliverables(
    opportunity_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[DeliverableRead]:
    """List all generated deliverables for an opportunity."""
    return [
        DeliverableRead.model_validate(d)
        for d in service.list_deliverables(db, opportunity_id)
    ]


@router.get("/{opportunity_id}/deliverables/{kind}", response_model=DeliverableRead)
def get_deliverable(
    opportunity_id: uuid.UUID, kind: DeliverableKind, db: Session = Depends(get_db)
) -> DeliverableRead:
    """Return the latest deliverable of a given kind."""
    deliverable = service.latest_deliverable(db, opportunity_id, kind)
    if deliverable is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Deliverable not generated yet")
    return DeliverableRead.model_validate(deliverable)
