#!/usr/bin/env bash

set -euo pipefail

COMPOSE_FILE="docker-compose.yml"
STATE_FILE="deploy/.active-color"
NGINX_CONFIG="deploy/nginx/default.conf"

if [[ -f "$STATE_FILE" ]]; then
    ACTIVE_COLOR=$(cat "$STATE_FILE")
else
    ACTIVE_COLOR="blue"
fi

if [[ "$ACTIVE_COLOR" == "blue" ]]; then
    INACTIVE_COLOR="green"
else
    INACTIVE_COLOR="blue"
fi

ACTIVE_SERVICE="app-${ACTIVE_COLOR}"
INACTIVE_SERVICE="app-${INACTIVE_COLOR}"

echo "Active color: $ACTIVE_COLOR"
echo "Deploying into: $INACTIVE_COLOR"

docker compose -f "$COMPOSE_FILE" up -d redis nginx

docker compose -f "$COMPOSE_FILE" \
    --profile "$INACTIVE_COLOR" \
    up -d "$INACTIVE_SERVICE"

CONTAINER_ID=$(
    docker compose -f "$COMPOSE_FILE" \
        --profile "$INACTIVE_COLOR" \
        ps -q "$INACTIVE_SERVICE"
)

echo "Waiting for $INACTIVE_SERVICE..."

READY=false

for i in {1..15}; do
    STATUS=$(docker inspect \
        --format='{{.State.Health.Status}}' \
        "$CONTAINER_ID" 2>/dev/null || echo "starting")

    echo "Attempt $i: $STATUS"

    if [[ "$STATUS" == "healthy" ]]; then
        READY=true
        break
    fi

    sleep 2
done

if [[ "$READY" != "true" ]]; then
    echo "Deployment failed: unhealthy container"

    docker compose \
        --profile "$INACTIVE_COLOR" \
        stop "$INACTIVE_SERVICE"

    exit 1
fi

echo "Running smoke test..."

if ! docker compose \
    --profile "$INACTIVE_COLOR" \
    exec -T "$INACTIVE_SERVICE" \
    python -c \
    "import urllib.request,json; d=json.load(urllib.request.urlopen('http://localhost:5000/status')); assert d['deploy_color']=='$INACTIVE_COLOR'"; then

    echo "Smoke test failed"

    docker compose \
        --profile "$INACTIVE_COLOR" \
        stop "$INACTIVE_SERVICE"

    exit 1
fi

echo "Switching nginx to $INACTIVE_COLOR..."

cat > "$NGINX_CONFIG" <<EOF
server {
    listen 80;

    location / {
        resolver 127.0.0.11 valid=5s;
        set \$backend "app-${INACTIVE_COLOR}:5000";

        proxy_pass http://\$backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

docker compose exec -T nginx nginx -s reload

echo "$INACTIVE_COLOR" > "$STATE_FILE"

docker compose \
    --profile "$ACTIVE_COLOR" \
    stop "$ACTIVE_SERVICE" || true

echo "Deployment successful"
echo "Active color: $INACTIVE_COLOR"
