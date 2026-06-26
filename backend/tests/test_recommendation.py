"""Tests for the recommendation engine (Epic 5)."""

from fastapi.testclient import TestClient

from app.models.recommendation import RecommendationType
from app.recommendation.engine import recommend


def test_engine_defers_on_low_confidence() -> None:
    rec_type, rationale = recommend(
        final_score=8.0, confidence=0.3, risk_score=1.0, feasibility_score=9.0
    )
    assert rec_type is RecommendationType.DEFER
    assert "incomplete" in rationale


def test_engine_do_not_pursue_on_low_score_or_high_risk() -> None:
    low_value = recommend(final_score=2.0, confidence=0.9, risk_score=1.0, feasibility_score=8.0)[0]
    high_risk = recommend(final_score=7.0, confidence=0.9, risk_score=8.0, feasibility_score=8.0)[0]
    assert low_value is RecommendationType.DO_NOT_PURSUE
    assert high_risk is RecommendationType.DO_NOT_PURSUE


def test_engine_conditions_on_low_feasibility() -> None:
    rec_type = recommend(final_score=5.0, confidence=0.9, risk_score=2.0, feasibility_score=4.0)[0]
    assert rec_type is RecommendationType.PROCEED_WITH_CONDITIONS


def test_engine_proceeds_when_strong() -> None:
    rec_type = recommend(final_score=6.0, confidence=1.0, risk_score=0.0, feasibility_score=10.0)[0]
    assert rec_type is RecommendationType.PROCEED


def _opp(client: TestClient) -> str:
    return client.post("/opportunities", json={"title": "Support Automation"}).json()["id"]


def _score(client: TestClient, opp_id: str) -> None:
    client.post(
        f"/opportunities/{opp_id}/score",
        json={"impact": 8, "ease": 6, "strategic_alignment": 9},
    )


def test_recommendation_requires_score(client: TestClient) -> None:
    opp_id = _opp(client)
    resp = client.post(f"/opportunities/{opp_id}/recommendation")
    assert resp.status_code == 409


def test_recommendation_unknown_opportunity_404(client: TestClient) -> None:
    resp = client.post("/opportunities/00000000-0000-0000-0000-000000000000/recommendation")
    assert resp.status_code == 404


def test_recommendation_proceed_full_flow(client: TestClient) -> None:
    opp_id = _opp(client)
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    for answer in ["3000/wk", "5 min", "2y history", "Jane"]:
        client.post(f"/opportunities/{opp_id}/continue", json={"answer": answer})
    _score(client, opp_id)

    resp = client.post(f"/opportunities/{opp_id}/recommendation")
    assert resp.status_code == 201
    body = resp.json()
    assert body["type"] == "PROCEED"
    assert body["confidence"] == 1.0
    assert body["score_snapshot_id"]

    assert client.get(f"/opportunities/{opp_id}").json()["status"] == "RECOMMENDED"
    assert client.get(f"/opportunities/{opp_id}/recommendation").json()["type"] == ("PROCEED")


def test_recommendation_defers_on_partial_context(client: TestClient) -> None:
    opp_id = _opp(client)
    client.post(f"/opportunities/{opp_id}/interview", json={"message": "too many emails"})
    client.post(f"/opportunities/{opp_id}/continue", json={"answer": "3000/wk"})
    _score(client, opp_id)  # confidence 0.25

    body = client.post(f"/opportunities/{opp_id}/recommendation").json()
    assert body["type"] == "DEFER"
