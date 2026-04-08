"""Filesystem helpers for Phase 1 ingestion."""

from __future__ import annotations

from glob import glob
from pathlib import Path

from synapse.domain import DocumentRecord


def resolve_ingest_sources(source_uri: str) -> list[Path]:
    """Resolve a single PDF, directory, or glob into concrete PDF paths."""

    expanded = Path(source_uri).expanduser()
    if any(token in source_uri for token in ("*", "?", "[")):
        matches = sorted(Path(match) for match in glob(str(expanded), recursive=True))
    elif expanded.is_file():
        matches = [expanded]
    elif expanded.is_dir():
        matches = sorted(path for path in expanded.rglob("*.pdf") if path.is_file())
    else:
        raise FileNotFoundError(f"ingest source does not exist: {source_uri}")

    if not matches:
        raise FileNotFoundError(f"ingest source matched no pdf files: {source_uri}")

    invalid = [path for path in matches if path.suffix.lower() != ".pdf"]
    if invalid:
        joined = ", ".join(str(path) for path in invalid)
        raise ValueError(f"ingest accepts only .pdf sources: {joined}")

    return matches


def write_document_records(records: list[DocumentRecord], output_uri: str | Path) -> list[Path]:
    """Write one or more document records to JSON files."""

    if not records:
        raise ValueError("write_document_records requires at least one record")

    output_path = Path(output_uri).expanduser()
    if len(records) > 1 and output_path.suffix.lower() == ".json":
        raise ValueError("batch ingest output must be a directory, not a single .json file")

    if len(records) == 1 and output_path.suffix.lower() == ".json":
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(records[0].model_dump_json(indent=2), encoding="utf-8")
        return [output_path]

    output_path.mkdir(parents=True, exist_ok=True)
    written_paths: list[Path] = []
    for record in records:
        target = output_path / f"{record.document_id}.json"
        target.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        written_paths.append(target)
    return written_paths
