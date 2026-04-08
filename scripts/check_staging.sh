#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/deploy/.env.staging"
COMPOSE_FILE="${ROOT_DIR}/deploy/docker-compose.staging.yml"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy deploy/.env.staging.example and fill the values first." >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

PROJECT_NAME="${COMPOSE_PROJECT_NAME:-synapse-testing}"
APP_URL="http://127.0.0.1:${SYNAPSE_STAGING_HTTP_PORT:-18080}"
export APP_URL

docker compose \
  --project-name "${PROJECT_NAME}" \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  ps

python - <<'PY'
import json
import os
import sys
import urllib.request

base_url = os.environ["APP_URL"].rstrip("/")

for path in ("/health", "/ready", "/info"):
    with urllib.request.urlopen(f"{base_url}{path}", timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    print(f"{path}:")
    print(json.dumps(payload, indent=2, sort_keys=True))

PY

docker compose \
  --project-name "${PROJECT_NAME}" \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  exec -T app python -m synapse doctor
