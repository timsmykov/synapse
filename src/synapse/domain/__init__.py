"""Canonical Synapse domain models."""

from .artifacts import (
    Artifact,
    DocumentArtifact,
    DocumentRecord,
    FigureArtifact,
    FormulaArtifact,
    Section,
    TableArtifact,
    TableCell,
)
from .provenance import BoundingBox, Citation, Provenance
from .tasks import (
    AnalyzeTaskRequest,
    IngestTaskRequest,
    QueryTaskRequest,
    TaskReceipt,
    TaskRequest,
)

__all__ = [
    "AnalyzeTaskRequest",
    "Artifact",
    "BoundingBox",
    "Citation",
    "DocumentArtifact",
    "DocumentRecord",
    "FigureArtifact",
    "FormulaArtifact",
    "IngestTaskRequest",
    "Provenance",
    "QueryTaskRequest",
    "Section",
    "TableArtifact",
    "TableCell",
    "TaskReceipt",
    "TaskRequest",
]
