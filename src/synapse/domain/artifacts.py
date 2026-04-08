"""Canonical artifact shapes for Synapse research workflows."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .common import SynapseModel
from .provenance import Citation, Provenance


class DocumentArtifact(SynapseModel):
    """Base shape for traceable content extracted from a source document."""

    artifact_id: str
    document_id: str
    artifact_type: str
    provenance: Provenance
    text: str | None = None
    order: int = Field(default=0, ge=0)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class Section(DocumentArtifact):
    artifact_type: Literal["section"] = "section"
    heading: str | None = None
    level: int = Field(ge=1)
    text: str


class TableCell(DocumentArtifact):
    artifact_type: Literal["table_cell"] = "table_cell"
    row_index: int = Field(alias="row", ge=1)
    column_index: int = Field(alias="column", ge=1)
    row_span: int = Field(default=1, ge=1)
    column_span: int = Field(default=1, ge=1)
    normalized_value: str | int | float | bool | None = None


class TableArtifact(DocumentArtifact):
    artifact_type: Literal["table"] = "table"
    caption: str | None = None
    label: str | None = None
    rows: int = Field(ge=1)
    columns: int = Field(ge=1)
    cells: list[TableCell] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_cells(self) -> TableArtifact:
        if not self.cells:
            raise ValueError("table artifacts require at least one cell")

        for cell in self.cells:
            if cell.row_index > self.rows:
                raise ValueError("table cell row_index exceeds table row count")
            if cell.column_index > self.columns:
                raise ValueError("table cell column_index exceeds table column count")
        return self


class FormulaArtifact(DocumentArtifact):
    artifact_type: Literal["formula"] = "formula"
    latex: str
    display_mode: bool = False
    mathml: str | None = None
    symbol_names: list[str] = Field(default_factory=list)


class FigureArtifact(DocumentArtifact):
    artifact_type: Literal["figure"] = "figure"
    caption: str | None = None
    figure_type: Literal["chart", "diagram", "plot", "photo", "scan", "unknown"] = "unknown"
    image_ref: str | None = None
    alt_text: str | None = None
    ocr_text: str | None = None


Artifact = Annotated[
    Section | TableCell | TableArtifact | FormulaArtifact | FigureArtifact,
    Field(discriminator="artifact_type"),
]


class DocumentRecord(SynapseModel):
    """Top-level record for a scientific source document."""

    document_id: str
    title: str
    source_uri: str | None = None
    source_format: str = "pdf"
    authors: list[str] = Field(default_factory=list)
    year: int | None = Field(default=None, ge=1000, le=9999)
    doi: str | None = None
    abstract: str | None = None
    provenance: Provenance | None = None
    citation: Citation | None = None
    artifacts: list[Artifact] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_document_provenance(self) -> DocumentRecord:
        if self.provenance is not None and self.provenance.source_document_id != self.document_id:
            raise ValueError("document provenance source_document_id must match document_id")
        return self
