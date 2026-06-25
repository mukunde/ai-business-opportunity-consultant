"""API tests for the Opportunity CRUD endpoints (Epic 1 / Milestone M1)."""

from fastapi.testclient import TestClient


def test_create_opportunity_defaults_to_draft(client: TestClient) -> None:
    response = client.post(
        "/opportunities",
        json={"title": "Customer Support Automation", "business_area": "Support"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Customer Support Automation"
    assert body["business_area"] == "Support"
    assert body["status"] == "DRAFT"
    assert body["current_version"] == 1
    assert body["id"]
    assert body["created_at"]


def test_create_requires_title(client: TestClient) -> None:
    response = client.post("/opportunities", json={"business_area": "Support"})
    assert response.status_code == 422


def test_get_opportunity(client: TestClient) -> None:
    created = client.post("/opportunities", json={"title": "Email Triage"}).json()
    response = client.get(f"/opportunities/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_unknown_returns_404(client: TestClient) -> None:
    response = client.get("/opportunities/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_opportunities(client: TestClient) -> None:
    client.post("/opportunities", json={"title": "A"})
    client.post("/opportunities", json={"title": "B"})
    response = client.get("/opportunities")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_opportunity_status(client: TestClient) -> None:
    created = client.post("/opportunities", json={"title": "Triage"}).json()
    response = client.patch(
        f"/opportunities/{created['id']}",
        json={"status": "INTERVIEW_ACTIVE"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "INTERVIEW_ACTIVE"


def test_update_rejects_invalid_status(client: TestClient) -> None:
    created = client.post("/opportunities", json={"title": "Triage"}).json()
    response = client.patch(f"/opportunities/{created['id']}", json={"status": "NOT_A_STATUS"})
    assert response.status_code == 422


def test_delete_opportunity(client: TestClient) -> None:
    created = client.post("/opportunities", json={"title": "Throwaway"}).json()
    assert client.delete(f"/opportunities/{created['id']}").status_code == 204
    assert client.get(f"/opportunities/{created['id']}").status_code == 404
