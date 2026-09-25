import os
import time

import redis
from flask import Flask, jsonify, request, Response, g

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST


app = Flask(__name__)

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


ALERT_THRESHOLD = 25


def alert_threshold():
    """Seuil d'alerte au-dessus duquel une notification est declenchee."""
    return ALERT_THRESHOLD


def sanitize_input(value):
    """Echappe les caracteres dangereux d'une entree utilisateur."""
    return value.replace("<", "&lt;").replace(">", "&gt;")


@app.before_request
def start_timer():
    g.start_time = time.perf_counter()


@app.route("/health")
def health():
    try:
        client = get_redis_client()
        client.ping()

        return jsonify(
            status="ok",
            redis="ok",
        ), 200

    except redis.RedisError:
        return jsonify(
            status="error",
            redis="unavailable",
        ), 503


@app.route("/status")
def status():
    return jsonify(
        service="projet-devops-groupe-demo",
        version="1.0",
        deploy_color=os.getenv("DEPLOY_COLOR", "unknown"),
        commit_sha=os.getenv("COMMIT_SHA", "local"),
    ), 200


@app.route("/visits")
def visits():
    client = get_redis_client()
    count = client.incr("visits")
    return jsonify(visits=count), 200


@app.route("/simulate-error")
def simulate_error():
    return jsonify(error="simulated failure"), 500


@app.after_request
def record_request(response):
    if request.path != "/metrics":
        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code,
        ).inc()

        duration = time.perf_counter() - g.start_time

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.path,
        ).observe(duration)

    return response


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
