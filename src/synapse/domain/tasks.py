"""Task request and response models for CLI/API orchestration."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from .common import SynapseModel


class TaskRequest(SynapseModel):
    """Base task shape shared by ingest/query/analyze workflows."""

    task_id: str | None = None
    task_type: str


class IngestTaskRequest(TaskRequest):
    task_type: Literal["ingest"] = "ingest"
    source_uri: str
    parser: str = "docling"
    force: bool = False


class QueryTaskRequest(TaskRequest):
    task_type: Literal["query"] = "query"
    query: str
    top_k: int = Field(default=5, ge=1, le=100)
    document_id: str | None = None


class AnalyzeTaskRequest(TaskRequest):
    task_type: Literal["analyze"] = "analyze"
    corpus_id: str | None = None
    analysis_mode: str = "systematic-review"


class TaskReceipt(SynapseModel):
    """Response model returned when a task is accepted or completed."""

    task_id: str
    task_type: str
    status: Literal["queued", "running", "succeeded", "failed"] = "queued"
    message: str | None = None
    document_id: str | None = None
    artifact_count: int = Field(default=0, ge=0)
    result: dict[str, Any] = Field(default_factory=dict)

    def as_command_payload(self) -> dict[str, Any]:
        """Compatibility view used by older workflow tests and callers."""

        payload = {"command": self.task_type}
        payload.update(self.result)
        return payload

    def __eq__(self, other: Any) -> bool:  # type: ignore[override]
        if isinstance(other, dict):
            return self.as_command_payload() == other
        return super().__eq__(other)
