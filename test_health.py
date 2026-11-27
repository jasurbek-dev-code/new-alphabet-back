from fastapi.testclient import TestClient

from database import get_db
from main import app, fastapi_app


client = TestClient(app)


def test_root_health_check_supports_get_and_head():
    get_response = client.get("/")
    head_response = client.head("/")

    assert get_response.status_code == 200
    assert get_response.json()["health"] == "/health"
    assert head_response.status_code == 200
    assert head_response.content == b""


def test_health_endpoint_supports_get_and_head():
    get_response = client.get("/health")
    head_response = client.head("/health")

    assert get_response.status_code == 200
    assert get_response.json()["status"] == "healthy"
    assert head_response.status_code == 200
    assert head_response.content == b""


def test_unhandled_errors_include_cors_headers():
    async def fail_db():
        raise RuntimeError("Simulated database failure")

    fastapi_app.dependency_overrides[get_db] = fail_db
    try:
        error_client = TestClient(app, raise_server_exceptions=False)
        response = error_client.post(
            "/api/v1/auth/sync",
            json={"init_data": "test"},
            headers={"Origin": "https://new-alphabet-front-gray.vercel.app"},
        )
    finally:
        fastapi_app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == "https://new-alphabet-front-gray.vercel.app"
