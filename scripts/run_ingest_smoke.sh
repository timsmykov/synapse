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
OUTPUT_DIR="$(read_env_value "SYNAPSE_SMOKE_OUTPUT_DIR" "data/ingest-smoke")"

FIXTURE_PATH="${ROOT_DIR}/test_corpus/smoke-fixture.pdf"
mkdir -p "$(dirname "${FIXTURE_PATH}")" "${ROOT_DIR}/${OUTPUT_DIR}"

cat > "${FIXTURE_PATH}" <<'EOF'
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 68 >>
stream
BT
/F1 18 Tf
36 96 Td
(Synapse smoke fixture) Tj
0 -24 Td
(CLI-first ingest check) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000241 00000 n 
0000000359 00000 n 
trailer
<< /Root 1 0 R /Size 6 >>
startxref
429
%%EOF
EOF

docker compose \
  --project-name "${PROJECT_NAME}" \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE}" \
  exec -T app \
  python -m synapse ingest \
  /workspace/test_corpus/smoke-fixture.pdf \
  "/workspace/${OUTPUT_DIR}"

echo
find "${ROOT_DIR}/${OUTPUT_DIR}" -maxdepth 1 -type f -name '*.json' | sort | sed -n '1,20p'
