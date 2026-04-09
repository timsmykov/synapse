#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/deploy/.env.staging"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy deploy/.env.staging.example and fill the values first." >&2
  exit 1
fi

read_env_value() {
  local key="$1"
  local default_value="$2"
  local value

  value="$(grep -E "^${key}=" "${ENV_FILE}" | head -n1 | cut -d= -f2- || true)"
  if [[ -z "${value}" ]]; then
    printf '%s\n' "${default_value}"
    return
  fi
  printf '%s\n' "${value}"
}

PROJECT_NAME="$(read_env_value "COMPOSE_PROJECT_NAME" "synapse-testing")"
NETWORK_NAME="${PROJECT_NAME}_default"
SERVER_CORPUS_DIR="$(read_env_value "SYNAPSE_SERVER_CORPUS_DIR" "/srv/synapse/test_corpus")"
GROBID_URL="$(read_env_value "SYNAPSE_GROBID_URL" "http://grobid:8070")"
OUTPUT_DIR="${1:-data/ingest-golden-isolated}"
SOURCE_PATTERN="${2:-${SERVER_CORPUS_DIR}/golden/*.pdf}"
CONTAINER_NAME="${3:-synapse-golden-isolated}"
IMAGE_NAME="${SYNAPSE_IMAGE:-synapse-testing:latest}"
HOST_HF_CACHE="${HF_HOME:-/srv/synapse/model-cache/hf}"
HOST_RAPIDOCR_CACHE="${SYNAPSE_RAPIDOCR_MODEL_DIR:-/srv/synapse/model-cache/rapidocr}"

mkdir -p "${ROOT_DIR}/${OUTPUT_DIR}"
find "${ROOT_DIR}/${OUTPUT_DIR}" -maxdepth 1 -type f -name '*.json' -delete

if ! docker network inspect "${NETWORK_NAME}" >/dev/null 2>&1; then
  echo "Missing Docker network ${NETWORK_NAME}. Bring up the staging stack first." >&2
  exit 1
fi

DOCKER_ARGS=(
  --rm
  --name "${CONTAINER_NAME}"
  --network "${NETWORK_NAME}"
  --env-file "${ENV_FILE}"
  -e "SYNAPSE_GROBID_URL=${GROBID_URL}"
  -v "${ROOT_DIR}:/workspace"
  -v "${SERVER_CORPUS_DIR}:${SERVER_CORPUS_DIR}:ro"
)

if [[ -d "${HOST_HF_CACHE}" ]]; then
  DOCKER_ARGS+=(-e "HF_HOME=/cache/hf" -v "${HOST_HF_CACHE}:/cache/hf")
fi

if [[ -d "${HOST_RAPIDOCR_CACHE}" ]]; then
  DOCKER_ARGS+=(-v "${HOST_RAPIDOCR_CACHE}:/usr/local/lib/python3.12/site-packages/rapidocr/models")
fi

docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true

docker run "${DOCKER_ARGS[@]}" \
  "${IMAGE_NAME}" \
  sh -lc "synapse ingest --source '${SOURCE_PATTERN}' --output '/workspace/${OUTPUT_DIR}'"

echo
find "${ROOT_DIR}/${OUTPUT_DIR}" -maxdepth 1 -type f -name '*.json' | sort | sed -n '1,40p'
