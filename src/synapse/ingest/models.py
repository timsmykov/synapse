"""Normalized intermediate parser outputs used by the Phase 1 ingest pipeline."""

from __future__ import annotations

from pydantic import Field

from synapse.domain.common import SynapseModel
from synapse.domain.provenance import BoundingBox


class ParsedSection(SynapseModel):
    heading: str | None = None
    level: int = Field(default=1, ge=1)
    text: str
    page_number: int = Field(default=1, ge=1)
    bbox: BoundingBox | None = None


class ParsedTableCell(SynapseModel):
    row: int = Field(ge=1)
    column: int = Field(ge=1)
    value: str | int | float | bool | None = None
    page_number: int = Field(default=1, ge=1)
    bbox: BoundingBox | None = None


class ParsedTable(SynapseModel):
    caption: str | None = None
    label: str | None = None
    rows: int = Field(ge=1)
    columns: int = Field(ge=1)
    page_number: int = Field(default=1, ge=1)
    bbox: BoundingBox | None = None
    cells: list[ParsedTableCell] = Field(default_factory=list)


class ParsedFormula(SynapseModel):
    latex: str
    page_number: int = Field(default=1, ge=1)
    bbox: BoundingBox | None = None
    display_mode: bool = False


class ParsedFigure(SynapseModel):
    caption: str | None = None
    figure_type: str = "unknown"
    page_number: int = Field(default=1, ge=1)
    bbox: BoundingBox | None = None
    image_ref: str | None = None
    alt_text: str | None = None


class DoclingParseResult(SynapseModel):
    document_id: str
    title: str | None = None
    source_uri: str
    sections: list[ParsedSection] = Field(default_factory=list)
    tables: list[ParsedTable] = Field(default_factory=list)
    formulas: list[ParsedFormula] = Field(default_factory=list)
    figures: list[ParsedFigure] = Field(default_factory=list)
    raw_payload: dict = Field(default_factory=dict)


class GrobidMetadataResult(SynapseModel):
    source_uri: str
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    year: int | None = Field(default=None, ge=1000, le=9999)
    doi: str | None = None
    abstract: str | None = None
    raw_tei: str | None = None
