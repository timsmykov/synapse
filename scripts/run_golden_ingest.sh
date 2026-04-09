#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/deploy/.env.staging"
COMPOSE_FILE="${ROOT_DIR}/deploy/docker-compose.staging.yml"

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
SERVER_CORPUS_DIR="$(read_env_value "SYNAPSE_SERVER_CORPUS_DIR" "/srv/synapse/test_corpus")"
OUTPUT_DIR="${1:-data/ingest-golden}"
SOURCE_PATTERN="${2:-${SERVER_CORPUS_DIR}/golden/*.pdf}"

mkdir -p "${ROOT_DIR}/${OUTPUT_DIR}"
find "${ROOT_DIR}/${OUTPUT_DIR}" -maxdepth 1 -type f -name '*.json' -delete

shopt -s nullglob
sources=(${SOURCE_PATTERN})
shopt -u nullglob

if [[ ${#sources[@]} -eq 0 ]]; then
  echo "No sources matched: ${SOURCE_PATTERN}" >&2
  exit 1
fi

run_index=0
for source_path in "${sources[@]}"; do
  run_index=$((run_index + 1))
  log_path="${ROOT_DIR}/${OUTPUT_DIR}/run-$(printf '%02d' "${run_index}").log"

  echo "Running ingest for ${source_path}"
  docker compose \
    --project-name "${PROJECT_NAME}" \
    --env-file "${ENV_FILE}" \
    -f "${COMPOSE_FILE}" \
    exec -T app \
    sh -lc "synapse ingest --source '${source_path}' --output '/workspace/${OUTPUT_DIR}'" \
    | tee "${log_path}"
done

echo
find "${ROOT_DIR}/${OUTPUT_DIR}" -maxdepth 1 -type f -name '*.json' | sort | sed -n '1,40p'
