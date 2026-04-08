"""Shared runtime reporting models for Synapse entrypoints."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from synapse.domain.common import SynapseModel
from synapse.runtime_health import RuntimeHealthCheck


class DoctorReport(SynapseModel):
    """Snapshot of the current runtime configuration."""

    command: Literal["doctor"] = "doctor"
    status: Literal["ok", "warn", "fail"] = "ok"
    app_name: str
    environment: str
    version: str
    deployment_target: str
    public_base_url: str | None = None
    reverse_proxy: str
    data_dir: str
    corpus_dir: str
    eval_dir: str
    database_url: str
    redis_url: str
    minio_endpoint: str
    minio_bucket: str
    grobid_url: str
    llm_provider: str
    default_parser: str
    default_embedding_model: str
    ingest_concurrency: int
    service_endpoints: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    checks: list[RuntimeHealthCheck] = Field(default_factory=list)
    notes: str | None = Field(default=None)
