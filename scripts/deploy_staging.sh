#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/deploy/.env.staging"
COMPOSE_FILE="${ROOT_DIR}/deploy/docker-compose.staging.yml"
PROJECT_NAME="${COMPOSE_PROJECT_NAME:-synapse-testing}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy deploy/.env.staging.example and fill the values first." >&2
  exit 1
fi

echo "Deploying Synapse testing stack with project name: ${PROJECT_NAME}"
docker compose \
  --project-name "${PROJECT_NAME}" \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  up -d --build

echo
docker compose \
  --project-name "${PROJECT_NAME}" \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  ps
