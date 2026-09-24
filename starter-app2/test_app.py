import redis
import app as app_module
from app import alert_threshold, sanitize_input, app


def test_alert_threshold():
    assert alert_threshold() == 25


def test_sanitize_input_escapes_html():
    assert sanitize_input("<script>") == "&lt;script&gt;"


def test_health_endpoint(monkeypatch):
    class FakeRedis:
        def ping(self):
            return True

    monkeypatch.setattr(
        app_module,
        "get_redis_client",
        lambda: FakeRedis()
    )

    client = app_module.app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health_endpoint_redis_down(monkeypatch):
    class BrokenRedis:
        def ping(self):
            raise redis.RedisError("Redis unavailable")

    monkeypatch.setattr(
        app_module,
        "get_redis_client",
        lambda: BrokenRedis()
    )

    client = app_module.app.test_client()
    response = client.get("/health")

    assert response.status_code == 503
    assert response.get_json()["status"] == "error"


def test_status_endpoint():
    client = app.test_client()
    response = client.get("/status")
    assert response.status_code == 200
    assert response.get_json()["service"] == "projet-devops-groupe-demo"
    assert response.get_json()["commit_sha"] == "local"
