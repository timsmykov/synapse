"""Ingestion boundary for Synapse.

Concrete Docling/GROBID/MinerU implementations should live in modules
under this package, not in CLI or API entrypoints.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .docling_adapter import DoclingAdapter, DoclingDependencyError
from .grobid_adapter import GrobidAdapter, GrobidDependencyError
from .io import resolve_ingest_sources, write_document_records
from .merge import merge_document_record
from .models import DoclingParseResult, GrobidMetadataResult

__all__ = [
    "DoclingAdapter",
    "DoclingDependencyError",
    "DoclingParseResult",
    "GrobidAdapter",
    "GrobidDependencyError",
    "GrobidMetadataResult",
    "IngestionAdapter",
    "merge_document_record",
    "resolve_ingest_sources",
    "write_document_records",
]


@runtime_checkable
class IngestionAdapter(Protocol):
    """Protocol for document ingestion adapters."""

    def ingest(self, source: str, **options: Any) -> dict[str, Any]:
        """Ingest a document source and return a structured result."""
