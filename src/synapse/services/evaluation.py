"""Golden corpus validation and baseline ingest evaluation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from synapse.domain import (
    DocumentRecord,
    FigureArtifact,
    FormulaArtifact,
    Section,
    TableArtifact,
    TableCell,
)
from synapse.domain.common import SynapseModel

CANONICAL_FIXTURE_NAMES = {
    "01-ecommerce-meta-analysis.pdf",
    "02-jams-service-review.pdf",
    "03-ebusiness-latent-topics.pdf",
    "04-chatbot-customer-experience.pdf",
    "05-ai-ethics-recommendation-systems.pdf",
}

ALLOWED_LAYOUT_FEATURES = {
    "tables",
    "merged_cells",
    "formulas",
    "figures",
    "charts",
    "multi_column",
    "citations",
}


class ExpectedArtifacts(SynapseModel):
    """Minimum artifact counts expected from the ingest pipeline."""

    sections: int = Field(ge=0)
    tables: int = Field(ge=0)
    table_cells: int = Field(ge=0)
    formulas: int = Field(ge=0)
    figures: int = Field(ge=0)
    citations: int = Field(ge=0)


class CorpusFixture(SynapseModel):
    """One golden corpus manifest entry."""

    document_id: str
    file_name: str
    domain: str
    source_file_name: str | None = None
    source_title: str | None = None
    page_count: int | None = Field(default=None, ge=1)
    layout_features: list[str] = Field(default_factory=list)
    expected_artifacts: ExpectedArtifacts
    notes: str | None = None

    @model_validator(mode="after")
    def _validate_layout_features(self) -> CorpusFixture:
        unknown = sorted(set(self.layout_features) - ALLOWED_LAYOUT_FEATURES)
        if unknown:
            raise ValueError(f"unknown layout features: {', '.join(unknown)}")
        if len(set(self.layout_features)) != len(self.layout_features):
            raise ValueError("layout_features must not contain duplicates")
        return self


class CorpusAuditReport(SynapseModel):
    """Audit of fixture metadata against a corpus directory."""

    manifest_path: str
    corpus_dir: str
    missing_files: list[str] = Field(default_factory=list)
    undocumented_files: list[str] = Field(default_factory=list)
    duplicate_document_ids: list[str] = Field(default_factory=list)
    duplicate_file_names: list[str] = Field(default_factory=list)
    canonical_name_gaps: list[str] = Field(default_factory=list)
    status: Literal["ok", "warn", "fail"] = "ok"


class MetricResult(SynapseModel):
    """Single ingest evaluation metric."""

    name: str
    value: float = Field(ge=0.0, le=1.0)
    target: float = Field(ge=0.0, le=1.0)
    passed: bool
    detail: str

    @property
    def score(self) -> float:
        """Compatibility alias used by the current test surface."""

        return self.value


class IngestEvaluationReport(SynapseModel):
    """Evaluation report for one fixture/document pair."""

    document_id: str
    fixture_file_name: str
    metrics: list[MetricResult] = Field(default_factory=list)
    passed: bool


def load_corpus_manifest(manifest_path: str | Path) -> list[CorpusFixture]:
    """Load and validate the corpus manifest JSON file."""

    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    return [CorpusFixture.model_validate(item) for item in payload]


def load_document_records(output_path: str | Path) -> list[DocumentRecord]:
    """Load one ingest JSON file or all JSON files from a directory."""

    raw_path = Path(output_path)
    files = sorted(raw_path.glob("*.json")) if raw_path.is_dir() else [raw_path]
    return [
        DocumentRecord.model_validate_json(file_path.read_text(encoding="utf-8"))
        for file_path in files
    ]


def audit_corpus_manifest(
    fixtures: list[CorpusFixture],
    *,
    manifest_path: str | Path,
    corpus_dir: str | Path,
) -> CorpusAuditReport:
    """Compare manifest entries against the local fixture directory."""

    manifest_location = Path(manifest_path)
    corpus_location = Path(corpus_dir)
    file_names = [fixture.file_name for fixture in fixtures]
    document_ids = [fixture.document_id for fixture in fixtures]
    present_files = sorted(path.name for path in corpus_location.glob("*.pdf"))

    missing_files = sorted(name for name in file_names if not (corpus_location / name).exists())
    undocumented_files = sorted(name for name in present_files if name not in set(file_names))
    duplicate_document_ids = sorted(_duplicates(document_ids))
    duplicate_file_names = sorted(_duplicates(file_names))
    canonical_name_gaps = sorted(
        name for name in CANONICAL_FIXTURE_NAMES if name not in set(file_names)
    )

    status: Literal["ok", "warn", "fail"] = "ok"
    if missing_files or duplicate_document_ids or duplicate_file_names:
        status = "fail"
    elif undocumented_files or canonical_name_gaps:
        status = "warn"

    return CorpusAuditReport(
        manifest_path=str(manifest_location),
        corpus_dir=str(corpus_location),
        missing_files=missing_files,
        undocumented_files=undocumented_files,
        duplicate_document_ids=duplicate_document_ids,
        duplicate_file_names=duplicate_file_names,
        canonical_name_gaps=canonical_name_gaps,
        status=status,
    )


def evaluate_document_record(
    record: DocumentRecord,
    fixture: CorpusFixture,
) -> IngestEvaluationReport:
    """Evaluate a structured ingest record against baseline Day 1 gates."""

    counts = _artifact_counts(record)
    table_score = _average(
        _count_similarity(counts["tables"], fixture.expected_artifacts.tables),
        _count_similarity(counts["table_cells"], fixture.expected_artifacts.table_cells),
    )
    formula_score = _count_similarity(counts["formulas"], fixture.expected_artifacts.formulas)
    provenance_score = _provenance_correctness(record)
    section_order_score = _section_order_correctness(record)

    metrics = [
        MetricResult(
            name="table_extraction_accuracy",
            value=table_score,
            target=0.95,
            passed=table_score >= 0.95,
            detail=(
                f"minimum expected tables={fixture.expected_artifacts.tables}, "
                f"actual tables={counts['tables']}; "
                f"minimum expected table_cells={fixture.expected_artifacts.table_cells}, "
                f"actual table_cells={counts['table_cells']}"
            ),
        ),
        MetricResult(
            name="formula_fidelity",
            value=formula_score,
            target=0.95,
            passed=formula_score >= 0.95,
            detail=(
                "minimum-count proxy for current baseline harness: "
                f"minimum expected formulas={fixture.expected_artifacts.formulas}, "
                f"actual formulas={counts['formulas']}"
            ),
        ),
        MetricResult(
            name="provenance_correctness",
            value=provenance_score,
            target=1.0,
            passed=provenance_score >= 1.0,
            detail=(
                "checks source_document_id, page_number, parser, confidence, "
                "and bbox page consistency"
            ),
        ),
        MetricResult(
            name="section_order_correctness",
            value=section_order_score,
            target=0.95,
            passed=section_order_score >= 0.95,
            detail=(
                "checks that section order values remain strictly increasing "
                "in emitted section sequence"
            ),
        ),
    ]

    return IngestEvaluationReport(
        document_id=record.document_id,
        fixture_file_name=fixture.file_name,
        metrics=metrics,
        passed=all(metric.passed for metric in metrics),
    )


def evaluate_ingest_outputs(
    manifest_path: str | Path,
    output_path: str | Path,
) -> list[IngestEvaluationReport]:
    """Evaluate one or more ingest JSON outputs against the corpus manifest."""

    fixtures = load_corpus_manifest(manifest_path)
    fixture_index = {fixture.document_id: fixture for fixture in fixtures}
    reports: list[IngestEvaluationReport] = []
    for record in load_document_records(output_path):
        fixture = fixture_index.get(record.document_id)
        if fixture is None:
            raise KeyError(
                f"document_id {record.document_id!r} is missing from the corpus manifest"
            )
        reports.append(evaluate_document_record(record, fixture))
    return reports


def _artifact_counts(record: DocumentRecord) -> dict[str, int]:
    sections = 0
    tables = 0
    table_cells = 0
    formulas = 0
    figures = 0
    citations = 1 if record.citation is not None else 0

    for artifact in record.artifacts:
        if isinstance(artifact, Section):
            sections += 1
        elif isinstance(artifact, TableArtifact):
            tables += 1
            table_cells += len(artifact.cells)
        elif isinstance(artifact, TableCell):
            table_cells += 1
        elif isinstance(artifact, FormulaArtifact):
            formulas += 1
        elif isinstance(artifact, FigureArtifact):
            figures += 1

    return {
        "sections": sections,
        "tables": tables,
        "table_cells": table_cells,
        "formulas": formulas,
        "figures": figures,
        "citations": citations,
    }


def _provenance_correctness(record: DocumentRecord) -> float:
    units = []
    for artifact in record.artifacts:
        units.append(artifact)
        if isinstance(artifact, TableArtifact):
            units.extend(artifact.cells)

    if not units:
        return 1.0

    valid = 0
    for unit in units:
        provenance = unit.provenance
        is_valid = (
            provenance.source_document_id == record.document_id
            and provenance.page_number >= 1
            and bool(provenance.parser)
            and provenance.confidence is not None
        )
        if provenance.bbox is not None:
            is_valid = is_valid and provenance.bbox.page_number == provenance.page_number
        if is_valid:
            valid += 1
    return valid / len(units)


def _section_order_correctness(record: DocumentRecord) -> float:
    sections = [artifact for artifact in record.artifacts if isinstance(artifact, Section)]
    if len(sections) <= 1:
        return 1.0

    transitions = 0
    valid_transitions = 0
    for previous, current in zip(sections, sections[1:], strict=False):
        transitions += 1
        if current.order > previous.order:
            valid_transitions += 1
    return valid_transitions / transitions if transitions else 1.0


def _count_similarity(actual: int, expected: int) -> float:
    if actual >= expected:
        return 1.0
    if expected == 0:
        return 1.0
    if actual == 0:
        return 0.0
    return actual / expected


def _average(*values: float) -> float:
    return sum(values) / len(values)


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        else:
            seen.add(value)
    return duplicates
