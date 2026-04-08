"""Ingestion boundary for Synapse.

Reserved for Day 1 ingestion work. Concrete Docling/GROBID/MinerU
implementations should live in modules under this package, not in CLI
or API entrypoints.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ["IngestionAdapter"]


@runtime_checkable
class IngestionAdapter(Protocol):
    """Protocol for document ingestion adapters."""

    def ingest(self, source: str, **options: Any) -> dict[str, Any]:
        """Ingest a document source and return a structured result."""
