"""Tests for the reporting engine (Epic 6)."""

from fastapi.testclient import TestClient

from app.reporting.generator import (
    ReportData,
    build_detailed_assessment,
    build_executive_summary,
)

_FULL_DATA = ReportData(
    title="Support Automation",
    problem_statement="Too many support emails.",
    summary="Classify and automate responses.",
    facts=[("Business Volume", "3000 per week")],
    assumptions=["Requests are repetitive"],
    unknowns=["Process Owner"],
    completeness={
        "business_context_score": 0.5,
        "process_understanding_score": 1.0,
        "data_readiness_score": 1.0,
        "roi_readiness_score": 1.0,
        "overall_score": 0.75,
    },
    score={
        "roi_score": 10.0,
        "impact_score": 8.0,
        "feasibility_score": 10.0,
        "risk_score": 1.5,
        "strategic_alignment_score": 9.0,
        "time_to_value_score": 10.0,
        "final_score": 6.5,
        "confidence": 0.75,
    },
    recommendation_type="PROCEED",
    recommendation_rationale="Strong opportunity.",
)


def test_executive_summary_has_sections() -> None:
    md = build_executive_summary(_FULL_DATA)
    assert "# Executive Summary: Support Automation" in md
    assert "## Business Problem" in md
    assert "## Recommendation" in md
    assert "PROCEED" in md
    assert "6.50 / 10" in md


def test_detailed_assessment_has_sections() -> None:
    md = build_detailed_assessment(_FULL_DATA)
    assert "## Context Collected" in md
    assert "Business Volume: 3000 per week" in md
    assert "## Assumptions" in md
    assert "Requests are repetitive" in md
    assert "| **Final** | **6.50** |" in md
    assert "PROCEED" in md


def test_reports_degrade_without_score() -> None:
    md = build_executive_summary(ReportData(title="Bare"))
    assert "Not scored yet." in md
    assert "No recommendation yet." in md


def _opp(client: TestClient) -> str:
    return client.post("/opportunities", json={"title": "Support Automation"}).json()["id"]


def _run_to_recommendation(client: TestClient, opp_id: str) -> None:
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    for answer in ["3000/wk", "5 min", "2y history", "Jane"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})
    client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )
    client.post(f"/opportunities/{opp_id}/recommendation")


def test_report_requires_recommendation(client: TestClient) -> None:
    opp_id = _opp(client)
    assert client.post(f"/opportunities/{opp_id}/report").status_code == 409


def test_report_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.post("/opportunities/00000000-0000-0000-0000-000000000000/report")
    assert resp.status_code == 404


def test_get_report_before_generation_404(client: TestClient) -> None:
    opp_id = _opp(client)
    assert client.get(f"/opportunities/{opp_id}/report").status_code == 404


def test_report_full_flow(client: TestClient) -> None:
    opp_id = _opp(client)
    _run_to_recommendation(client, opp_id)

    resp = client.post(f"/opportunities/{opp_id}/report")
    assert resp.status_code == 201
    bundle = resp.json()
    assert "# Executive Summary" in bundle["executive_summary"]["markdown_content"]
    assert "## Scoring" in bundle["detailed_assessment"]["markdown_content"]
    assert "PROCEED" in bundle["executive_summary"]["markdown_content"]

    # Opportunity advanced to REVIEW; the report is retrievable.
    assert client.get(f"/opportunities/{opp_id}").json()["status"] == "REVIEW"
    assert client.get(f"/opportunities/{opp_id}/report").status_code == 200
