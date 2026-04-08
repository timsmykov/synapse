"""Shared runtime reporting models for Synapse entrypoints."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from synapse.domain.common import SynapseModel


class DoctorReport(SynapseModel):
    """Snapshot of the current runtime configuration."""

    command: Literal["doctor"] = "doctor"
    app_name: str
    environment: str
    version: str
    data_dir: str
    corpus_dir: str
    eval_dir: str
    database_url: str
    redis_url: str
    minio_endpoint: str
    minio_bucket: str
    llm_provider: str
    default_parser: str
    default_embedding_model: str
    notes: str | None = Field(default=None)
