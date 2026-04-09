#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST_PATH="${MANIFEST_PATH:-${ROOT_DIR}/test_corpus/corpus-manifest.json}"
SOURCE_DIR="${GOLDEN_PDF_SOURCE_DIR:-/Users/timsmykov/Desktop/Статьи для теста}"
REMOTE_HOST="${REMOTE_HOST:-root@194.163.181.122}"
REMOTE_DIR="${REMOTE_DIR:-/srv/synapse/test_corpus/golden}"

if [[ ! -f "${MANIFEST_PATH}" ]]; then
  echo "Missing manifest: ${MANIFEST_PATH}" >&2
  exit 1
fi

if [[ ! -d "${SOURCE_DIR}" ]]; then
  echo "Missing source directory: ${SOURCE_DIR}" >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required for corpus sync." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

python3 - "${MANIFEST_PATH}" "${SOURCE_DIR}" "${TMP_DIR}" <<'PY'
import json
import shutil
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
source_dir = Path(sys.argv[2])
target_dir = Path(sys.argv[3])

entries = json.loads(manifest_path.read_text(encoding="utf-8"))
for entry in entries:
    source_path_value = entry.get("source_path")
    if source_path_value:
        source_path = Path(source_path_value).expanduser()
    else:
        source_name = entry.get("source_file_name") or entry["file_name"]
        source_path = source_dir / source_name
    if not source_path.exists():
        raise SystemExit(f"Missing source PDF: {source_path}")
    target_path = target_dir / entry["file_name"]
    shutil.copy2(source_path, target_path)

shutil.copy2(manifest_path, target_dir / "corpus-manifest.json")
PY

ssh "${REMOTE_HOST}" "mkdir -p '${REMOTE_DIR}'"
rsync -av --delete "${TMP_DIR}/" "${REMOTE_HOST}:${REMOTE_DIR}/"

echo "Synced golden corpus to ${REMOTE_HOST}:${REMOTE_DIR}"
