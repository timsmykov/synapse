"""Retrieval boundary for Synapse.

Reserved for hierarchical and hybrid retrieval work. Query adapters and
index builders should live here once the real MVP retrieval layer lands.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ["Retriever"]


@runtime_checkable
class Retriever(Protocol):
    """Protocol for structured research retrieval."""

    def query(self, prompt: str, **options: Any) -> dict[str, Any]:
        """Execute a retrieval query and return structured matches."""
