"""Merge normalized parser outputs into Synapse domain records."""

from __future__ import annotations

from synapse.domain import (
    Citation,
    DocumentRecord,
    FigureArtifact,
    FormulaArtifact,
    Provenance,
    Section,
    TableArtifact,
    TableCell,
)

from .models import DoclingParseResult, GrobidMetadataResult


def merge_document_record(
    structure: DoclingParseResult,
    metadata: GrobidMetadataResult | None = None,
) -> DocumentRecord:
    preferred_title = (
        metadata.title if metadata and metadata.title else structure.title
    ) or structure.document_id
    citation = None
    if metadata and metadata.title:
        citation = Citation(
            title=metadata.title,
            authors=metadata.authors,
            year=metadata.year,
            doi=metadata.doi,
            reference_text=metadata.abstract,
        )

    document_parser = "docling+grobid" if metadata is not None else "docling"

    document = DocumentRecord(
        document_id=structure.document_id,
        title=preferred_title,
        source_uri=structure.source_uri,
        authors=metadata.authors if metadata else [],
        year=metadata.year if metadata else None,
        doi=metadata.doi if metadata else None,
        abstract=metadata.abstract if metadata else None,
        citation=citation,
        provenance=Provenance(
            source_document_id=structure.document_id,
            page_number=1,
            source_document_title=preferred_title,
            parser=document_parser,
            source_uri=structure.source_uri,
            citation=citation,
        ),
        artifacts=[],
    )

    artifacts = []

    for index, section in enumerate(structure.sections, start=1):
        artifacts.append(
            Section(
                artifact_id=f"{structure.document_id}:section:{index}",
                document_id=structure.document_id,
                provenance=Provenance(
                    source_document_id=structure.document_id,
                    page_number=section.page_number,
                    source_document_title=document.title,
                    bbox=section.bbox,
                    parser="docling",
                    extraction_stage="structure",
                    confidence=section.confidence,
                    source_uri=structure.source_uri,
                    citation=citation,
                ),
                heading=section.heading,
                level=section.level,
                text=section.text,
                order=index,
            )
        )

    for table_index, table in enumerate(structure.tables, start=1):
        cells = []
        for cell_index, cell in enumerate(table.cells, start=1):
            cells.append(
                TableCell(
                    artifact_id=f"{structure.document_id}:table:{table_index}:cell:{cell_index}",
                    document_id=structure.document_id,
                    provenance=Provenance(
                        source_document_id=structure.document_id,
                        page_number=cell.page_number,
                        source_document_title=document.title,
                        bbox=cell.bbox,
                        parser="docling",
                        extraction_stage="table",
                        confidence=cell.confidence,
                        source_uri=structure.source_uri,
                        citation=citation,
                    ),
                    row=cell.row,
                    column=cell.column,
                    normalized_value=cell.value,
                )
            )
        if cells:
            artifacts.append(
                TableArtifact(
                    artifact_id=f"{structure.document_id}:table:{table_index}",
                    document_id=structure.document_id,
                    provenance=Provenance(
                        source_document_id=structure.document_id,
                        page_number=table.page_number,
                        source_document_title=document.title,
                        bbox=table.bbox,
                        parser="docling",
                        extraction_stage="table",
                        confidence=table.confidence,
                        source_uri=structure.source_uri,
                        citation=citation,
                    ),
                    caption=table.caption,
                    label=table.label,
                    rows=table.rows,
                    columns=table.columns,
                    cells=cells,
                )
            )

    for index, formula in enumerate(structure.formulas, start=1):
        artifacts.append(
            FormulaArtifact(
                artifact_id=f"{structure.document_id}:formula:{index}",
                document_id=structure.document_id,
                provenance=Provenance(
                    source_document_id=structure.document_id,
                    page_number=formula.page_number,
                    source_document_title=document.title,
                    bbox=formula.bbox,
                    parser="docling",
                    extraction_stage="formula",
                    confidence=formula.confidence,
                    source_uri=structure.source_uri,
                    citation=citation,
                ),
                latex=formula.latex,
                display_mode=formula.display_mode,
            )
        )

    for index, figure in enumerate(structure.figures, start=1):
        artifacts.append(
            FigureArtifact(
                artifact_id=f"{structure.document_id}:figure:{index}",
                document_id=structure.document_id,
                provenance=Provenance(
                    source_document_id=structure.document_id,
                    page_number=figure.page_number,
                    source_document_title=document.title,
                    bbox=figure.bbox,
                    parser="docling",
                    extraction_stage="figure",
                    confidence=figure.confidence,
                    source_uri=structure.source_uri,
                    citation=citation,
                ),
                caption=figure.caption,
                figure_type=figure.figure_type,
                image_ref=figure.image_ref,
                alt_text=figure.alt_text,
            )
        )

    document.artifacts = artifacts
    return document
