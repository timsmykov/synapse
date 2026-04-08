"""Storage boundary for Synapse.

Reserved for persistence adapters such as PostgreSQL, pgvector, Redis,
and MinIO. Keep storage behavior out of CLI/API entrypoints.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ["ArtifactStore"]


@runtime_checkable
class ArtifactStore(Protocol):
    """Protocol for storing and retrieving binary artifacts."""

    def put(self, key: str, payload: bytes, **metadata: Any) -> str:
        """Persist an artifact and return its storage reference."""

    def get(self, key: str) -> bytes:
        """Load an artifact by storage key."""
