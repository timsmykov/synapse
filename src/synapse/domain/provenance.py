"""Canonical provenance shapes for traceable document extraction."""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from .common import SynapseModel


class BoundingBox(SynapseModel):
    """PDF-space bounding box with page coordinates."""

    page_number: int = Field(alias="page", ge=1)
    x0: float = Field(ge=0)
    y0: float = Field(ge=0)
    x1: float = Field(ge=0)
    y1: float = Field(ge=0)
    page_width: float | None = Field(default=None, gt=0)
    page_height: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _validate_geometry(self) -> BoundingBox:
        if self.x1 <= self.x0:
            raise ValueError("x1 must be greater than x0")
        if self.y1 <= self.y0:
            raise ValueError("y1 must be greater than y0")
        return self


class Citation(SynapseModel):
    """Bibliographic citation attached to a document or extracted artifact."""

    citation_key: str | None = None
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = Field(default=None, ge=1000, le=9999)
    doi: str | None = None
    pmid: str | None = None
    pmcid: str | None = None
    url: str | None = None
    reference_text: str | None = None


class Provenance(SynapseModel):
    """Traceability metadata for a parsed artifact."""

    source_document_id: str
    page_number: int = Field(ge=1)
    source_document_title: str | None = None
    bbox: BoundingBox | None = None
    parser: str | None = None
    extraction_stage: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    source_uri: str | None = None
    source_sha256: str | None = None
    citation: Citation | None = None
    notes: str | None = None

    @field_validator("page_number")
    @classmethod
    def _validate_page_number(cls, value: int) -> int:
        if value < 1:
            raise ValueError("page_number must be >= 1")
        return value

    @model_validator(mode="after")
    def _validate_bbox_page(self) -> Provenance:
        if self.bbox is not None and self.bbox.page_number != self.page_number:
            raise ValueError("bbox.page_number must match provenance.page_number")
        return self
