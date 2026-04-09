"""Shared workflow functions used by interfaces."""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter

from synapse.config import Settings, get_settings
from synapse.domain import DocumentRecord
from synapse.domain.tasks import (
    AnalyzeTaskRequest,
    IngestTaskRequest,
    QueryTaskRequest,
    TaskReceipt,
)
from synapse.ingest import (
    DoclingAdapter,
    GrobidAdapter,
    GrobidDependencyError,
    merge_document_record,
    resolve_ingest_sources,
    write_document_records,
)
from synapse.runtime_health import build_runtime_health_report

from .reporting import DoctorReport


logger = logging.getLogger(__name__)


def ingest_workflow(request: IngestTaskRequest) -> TaskReceipt:
    try:
        resolved_sources = resolve_ingest_sources(request.source_uri)
    except FileNotFoundError as exc:
        return TaskReceipt(
            task_id=request.task_id or request.source_uri,
            task_type=request.task_type,
            status="failed",
            message=str(exc),
            result={
                **request.model_dump(mode="json"),
                "error": str(exc),
            },
        )

    warnings: list[str] = []
    documents: list[DocumentRecord] = []
    for source_path in resolved_sources:
        document, document_warnings = build_document_record(source_path)
        documents.append(document)
        warnings.extend(document_warnings)

    written_files = write_document_records(documents, request.output_uri)
    artifact_count = sum(len(document.artifacts) for document in documents)
    document_id = documents[0].document_id if len(documents) == 1 else None
    return TaskReceipt(
        task_id=request.task_id or request.source_uri,
        task_type=request.task_type,
        status="succeeded",
        message=f"Ingested {len(documents)} document(s) to {request.output_uri}",
        document_id=document_id,
        artifact_count=artifact_count,
        result={
            "source_uri": request.source_uri,
            "output_uri": request.output_uri,
            "parser": request.parser,
            "document_id": document_id,
            "documents": [document.document_id for document in documents],
            "artifact_count": artifact_count,
            "resolved_sources": [str(path) for path in resolved_sources],
            "written_files": [str(path) for path in written_files],
            "warnings": warnings,
        },
    )


def query_workflow(request: QueryTaskRequest) -> TaskReceipt:
    return TaskReceipt(
        task_id=request.task_id or request.query,
        task_type=request.task_type,
        message=f"Query prepared for top_k={request.top_k}",
        result=request.model_dump(mode="json"),
    )


def analyze_workflow(request: AnalyzeTaskRequest) -> TaskReceipt:
    return TaskReceipt(
        task_id=request.task_id or request.task_type,
        task_type=request.task_type,
        message=f"Analyze prepared for {request.analysis_mode}",
        result=request.model_dump(mode="json"),
    )


def doctor_workflow(settings: Settings | None = None) -> DoctorReport:
    runtime = settings or get_settings()
    summary = runtime.summary
    health = build_runtime_health_report(runtime)
    return DoctorReport(
        status=health.status,
        app_name=summary["app_name"],
        environment=summary["environment"],
        version=summary["version"],
        deployment_target=summary["deployment_target"],
        public_base_url=summary["public_base_url"] or None,
        reverse_proxy=summary["reverse_proxy"],
        data_dir=summary["data_dir"],
        corpus_dir=summary["corpus_dir"],
        eval_dir=summary["eval_dir"],
        database_url=summary["database_url"],
        redis_url=summary["redis_url"],
        minio_endpoint=summary["minio_endpoint"],
        minio_bucket=summary["minio_bucket"],
        grobid_url=summary["grobid_url"],
        llm_provider=summary["llm_provider"],
        default_parser=summary["default_parser"],
        default_embedding_model=summary["default_embedding_model"],
        ingest_concurrency=runtime.ingest_concurrency,
        service_endpoints=health.service_endpoints,
        warnings=health.warnings,
        checks=health.checks,
    )


def build_document_record(source_path: Path) -> tuple[DocumentRecord, list[str]]:
    warnings: list[str] = []
    settings = get_settings()
    logger.info(
        "Starting document build for %s with OCR %s",
        source_path.name,
        "enabled" if settings.parser_ocr_enabled else "disabled",
    )

    docling_started = perf_counter()
    docling = DoclingAdapter(ocr_enabled=settings.parser_ocr_enabled).convert(str(source_path))
    logger.info(
        "Docling conversion completed for %s in %.2fs",
        source_path.name,
        perf_counter() - docling_started,
    )

    grobid = None
    grobid_started = perf_counter()
    try:
        grobid = GrobidAdapter().extract(str(source_path))
        logger.info(
            "GROBID extraction completed for %s in %.2fs",
            source_path.name,
            perf_counter() - grobid_started,
        )
    except GrobidDependencyError as exc:
        hint = GrobidAdapter.runtime_hint(settings.grobid_url)
        message = f"{exc}{hint or ''}"
        warnings.append(message)
        logger.warning(
            "GROBID dependency unavailable for %s after %.2fs: %s",
            source_path.name,
            perf_counter() - grobid_started,
            message,
        )
    except Exception as exc:
        warnings.append(
            f"GROBID extraction failed for {source_path.name}: {exc}. "
            "Continuing with Docling-only ingest output."
        )
        logger.warning(
            "GROBID extraction failed for %s after %.2fs: %s",
            source_path.name,
            perf_counter() - grobid_started,
            exc,
        )
    return merge_document_record(docling, grobid), warnings
