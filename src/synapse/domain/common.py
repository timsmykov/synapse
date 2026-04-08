"""Shared Pydantic base classes for Synapse domain models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SynapseModel(BaseModel):
    """Base class for contract-first models used across CLI and API layers."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)

