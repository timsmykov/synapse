"""Shared use-case layer for CLI and API."""

from .evaluation import (
    CorpusAuditReport,
    CorpusFixture,
    ExpectedArtifacts,
    IngestCoverageError,
    IngestEvaluationReport,
    MetricResult,
    audit_corpus_manifest,
    evaluate_document_record,
    evaluate_ingest_outputs,
    load_corpus_manifest,
    load_document_records,
)
from .reporting import DoctorReport
from .workflows import analyze_workflow, doctor_workflow, ingest_workflow, query_workflow

__all__ = [
    "CorpusAuditReport",
    "CorpusFixture",
    "DoctorReport",
    "ExpectedArtifacts",
    "IngestCoverageError",
    "IngestEvaluationReport",
    "MetricResult",
    "analyze_workflow",
    "audit_corpus_manifest",
    "doctor_workflow",
    "evaluate_document_record",
    "evaluate_ingest_outputs",
    "ingest_workflow",
    "load_corpus_manifest",
    "load_document_records",
    "query_workflow",
]
