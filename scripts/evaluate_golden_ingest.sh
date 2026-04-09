#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_PATH="${1:-data/ingest-golden}"
MANIFEST_PATH="${2:-test_corpus/corpus-manifest.json}"

PYTHON_CANDIDATES=(
  "${SYNAPSE_REPO_PYTHON:-}"
  "${ROOT_DIR}/.venv/bin/python"
  "${ROOT_DIR}/../.venv/bin/python"
)

PYTHON_BIN=""
for candidate in "${PYTHON_CANDIDATES[@]}"; do
  if [[ -n "${candidate}" && -x "${candidate}" ]]; then
    PYTHON_BIN="${candidate}"
    break
  fi
done

if [[ -z "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi

if [[ -z "${PYTHON_BIN}" ]]; then
  echo "Unable to find a Python interpreter for evaluation." >&2
  echo "Set SYNAPSE_REPO_PYTHON or install the repo dependencies first." >&2
  exit 1
fi

cd "${ROOT_DIR}"
"${PYTHON_BIN}" scripts/evaluate_ingest.py "${OUTPUT_PATH}" --manifest "${MANIFEST_PATH}"
