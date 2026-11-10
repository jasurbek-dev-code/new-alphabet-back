from fastapi.testclient import TestClient

from main import app


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
