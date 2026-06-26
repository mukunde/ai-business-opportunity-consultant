"""Tests for the scoring engine (Epic 4): pure engine + API, driven by FakeLLM."""

from fastapi.testclient import TestClient

from app.scoring.engine import compute_scores


def test_engine_full_completeness() -> None:
    scores = compute_scores(
        {"overall_score": 1.0, "data_readiness_score": 1.0, "roi_readiness_score": 1.0},
        impact=8,
        ease=6,
        strategic_alignment=9,
    )
    assert scores["confidence"] == 1.0
    assert scores["roi_score"] == 10.0
    assert scores["feasibility_score"] == 10.0
    assert scores["risk_score"] == 0.0
    # ICE = 8 * 10 * 6 = 480 -> /100 = 4.8; final = .3*10 + .3*4.8 + .2*9 - .2*0
    assert scores["final_score"] == 6.24


def test_engine_partial_completeness_lowers_confidence_and_raises_risk() -> None:
    scores = compute_scores(
        {"overall_score": 0.25, "data_readiness_score": 0.0, "roi_readiness_score": 0.5},
        impact=8,
        ease=6,
        strategic_alignment=9,
    )
    assert scores["confidence"] == 0.25
    assert scores["risk_score"] == 8.75
    assert scores["final_score"] == 1.91


def _opp(client: TestClient) -> str:
    return client.post("/opportunities", json={"title": "Support Automation"}).json()["id"]


def _full_interview(client: TestClient, opp_id: str) -> None:
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    for answer in ["3000/wk", "5 min", "2y history", "Jane"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})


def test_score_requires_context(client: TestClient) -> None:
    opp_id = _opp(client)
    resp = client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )
    assert resp.status_code == 409


def test_score_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.post(
        "/opportunities/00000000-0000-0000-0000-000000000000/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )
    assert resp.status_code == 404


def test_score_validation(client: TestClient) -> None:
    opp_id = _opp(client)
    _full_interview(client, opp_id)
    resp = client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 0, "ease": 6, "strategic_alignment": 9},
    )
    assert resp.status_code == 422


def test_score_full_flow(client: TestClient) -> None:
    opp_id = _opp(client)
    _full_interview(client, opp_id)

    resp = client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["confidence"] == 1.0
    assert body["final_score"] == 6.24
    assert body["risk_score"] == 0.0

    # Opportunity advanced to SCORING, and the latest score is retrievable.
    assert client.get(f"/opportunities/{opp_id}").json()["status"] == "SCORING"
    assert client.get(f"/opportunities/{opp_id}/score").json()["final_score"] == 6.24


def test_get_score_before_scoring_404(client: TestClient) -> None:
    opp_id = _opp(client)
    assert client.get(f"/opportunities/{opp_id}/score").status_code == 404
