"""Research primitive boundary for Synapse.

Reserved for systematic-review primitives such as PICO extraction,
bias checks, table validation, and consistency analysis.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

__all__ = ["ResearchPrimitive"]


@runtime_checkable
class ResearchPrimitive(Protocol):
    """Protocol for reusable research primitives."""

    name: str

    def run(self, **options: Any) -> dict[str, Any]:
        """Execute the primitive and return structured output."""
