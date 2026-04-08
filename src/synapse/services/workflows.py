"""Shared workflow functions used by interfaces."""

from __future__ import annotations

from synapse.config import Settings, get_settings
from synapse.domain.tasks import (
    AnalyzeTaskRequest,
    IngestTaskRequest,
    QueryTaskRequest,
    TaskReceipt,
)

from .reporting import DoctorReport


def ingest_workflow(request: IngestTaskRequest) -> TaskReceipt:
    return TaskReceipt(
        task_id=request.task_id or request.source_uri,
        task_type=request.task_type,
        message=f"Ingest prepared for {request.source_uri}",
        result=request.model_dump(),
    )


def query_workflow(request: QueryTaskRequest) -> TaskReceipt:
    return TaskReceipt(
        task_id=request.task_id or request.query,
        task_type=request.task_type,
        message=f"Query prepared for top_k={request.top_k}",
        result=request.model_dump(),
    )


def analyze_workflow(request: AnalyzeTaskRequest) -> TaskReceipt:
    return TaskReceipt(
        task_id=request.task_id or request.task_type,
        task_type=request.task_type,
        message=f"Analyze prepared for {request.analysis_mode}",
        result=request.model_dump(),
    )


def doctor_workflow(settings: Settings | None = None) -> DoctorReport:
    runtime = settings or get_settings()
    summary = runtime.summary
    return DoctorReport(
        app_name=summary["app_name"],
        environment=summary["environment"],
        version=summary["version"],
        data_dir=summary["data_dir"],
        corpus_dir=summary["corpus_dir"],
        eval_dir=summary["eval_dir"],
        database_url=summary["database_url"],
        redis_url=summary["redis_url"],
        minio_endpoint=summary["minio_endpoint"],
        minio_bucket=summary["minio_bucket"],
        llm_provider=summary["llm_provider"],
        default_parser=summary["default_parser"],
        default_embedding_model=summary["default_embedding_model"],
    )
