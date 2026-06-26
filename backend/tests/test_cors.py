"""CORS middleware lets the Next.js dev origin call the API."""

from fastapi.testclient import TestClient


def test_cors_allows_frontend_origin(client: TestClient) -> None:
    resp = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_preflight(client: TestClient) -> None:
    resp = client.options(
        "/opportunities",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code in (200, 204)
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
