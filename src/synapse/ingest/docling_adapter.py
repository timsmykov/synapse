"""Docling adapter boundary for Synapse Phase 1 ingestion."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from synapse.domain.provenance import BoundingBox

from .models import (
    DoclingParseResult,
    ParsedFigure,
    ParsedFormula,
    ParsedSection,
    ParsedTable,
    ParsedTableCell,
)


class DoclingDependencyError(RuntimeError):
    """Raised when Docling integration is requested without the dependency installed."""


class DoclingAdapter:
    """Convert a PDF into normalized structural artifacts using Docling."""

    def __init__(self, converter_factory: Callable[[], Any] | None = None) -> None:
        self._converter_factory = converter_factory

    def convert(self, source_uri: str | Path) -> DoclingParseResult:
        source_path = Path(source_uri).expanduser()
        if not source_path.exists():
            raise FileNotFoundError(source_uri)

        converter = self._converter_factory() if self._converter_factory else self._load_converter()
        result = converter.convert(source_path)
        exported = self._export_document(self._extract_document(result))
        document_id = source_path.stem
        return DoclingParseResult(
            document_id=document_id,
            title=self._extract_title(exported) or document_id,
            source_uri=str(source_path),
            sections=self._extract_sections(exported),
            tables=self._extract_tables(exported),
            formulas=self._extract_formulas(exported),
            figures=self._extract_figures(exported),
            raw_payload=exported,
        )

    def _load_converter(self) -> Any:
        try:
            document_converter = self._import_document_converter()
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency optional.
            raise DoclingDependencyError(
                "Docling is not installed. Install `synapse[research]` or run "
                "`pip install docling` to enable Synapse PDF ingestion."
            ) from exc
        return document_converter.DocumentConverter()

    @staticmethod
    def _import_document_converter() -> Any:
        from docling import document_converter

        return document_converter

    @staticmethod
    def _extract_document(result: Any) -> Any:
        return getattr(result, "document", result)

    @staticmethod
    def _export_document(document: Any) -> dict:
        if hasattr(document, "export_to_dict"):
            exported = document.export_to_dict()
            if not isinstance(exported, dict):
                raise TypeError("Docling export_to_dict() must return a dictionary")
            return exported
        if hasattr(document, "model_dump"):
            return document.model_dump(mode="json", by_alias=True)
        if isinstance(document, dict):
            return document
        raise TypeError("Unsupported Docling document export shape")

    @staticmethod
    def _extract_title(exported: dict) -> str | None:
        return exported.get("title") or exported.get("name")

    @classmethod
    def _extract_sections(cls, exported: dict) -> list[ParsedSection]:
        items = exported.get("sections") or exported.get("texts") or exported.get("body") or []
        sections: list[ParsedSection] = []
        for item in items:
            text = item.get("text") or item.get("body") or item.get("orig")
            if not text:
                continue
            page_number = cls._page_number_from_item(item)
            sections.append(
                ParsedSection(
                    heading=item.get("heading") or item.get("title"),
                    level=item.get("level", 1),
                    text=text,
                    page_number=page_number,
                    bbox=cls._bbox_from_item(item, page_number),
                    confidence=cls._confidence_from_item(item),
                )
            )
        if not sections and exported.get("markdown"):
            sections.append(ParsedSection(text=exported["markdown"], page_number=1))
        return sections

    @classmethod
    def _extract_tables(cls, exported: dict) -> list[ParsedTable]:
        tables: list[ParsedTable] = []
        for item in exported.get("tables", []):
            table_page_number = cls._page_number_from_item(item)
            cells = [
                ParsedTableCell(
                    row=cell.get("row", 1),
                    column=cell.get("column", 1),
                    value=cell.get("value", cell.get("text")),
                    page_number=cls._page_number_from_item(cell, default=table_page_number),
                    bbox=cls._bbox_from_item(
                        cell,
                        cls._page_number_from_item(cell, default=table_page_number),
                    ),
                    confidence=cls._confidence_from_item(cell),
                )
                for cell in item.get("cells", [])
            ]
            if not cells:
                continue
            tables.append(
                ParsedTable(
                    caption=item.get("caption"),
                    label=item.get("label"),
                    rows=item.get("rows", max(cell.row for cell in cells)),
                    columns=item.get("columns", max(cell.column for cell in cells)),
                    page_number=table_page_number,
                    bbox=cls._bbox_from_item(item, table_page_number),
                    confidence=cls._confidence_from_item(item),
                    cells=cells,
                )
            )
        return tables

    @classmethod
    def _extract_formulas(cls, exported: dict) -> list[ParsedFormula]:
        formulas: list[ParsedFormula] = []
        for item in exported.get("formulas", []):
            latex = item.get("latex") or item.get("text")
            if not latex:
                continue
            page_number = cls._page_number_from_item(item)
            formulas.append(
                ParsedFormula(
                    latex=latex,
                    page_number=page_number,
                    bbox=cls._bbox_from_item(item, page_number),
                    display_mode=item.get("display_mode", False),
                    confidence=cls._confidence_from_item(item),
                )
            )
        return formulas

    @classmethod
    def _extract_figures(cls, exported: dict) -> list[ParsedFigure]:
        figures: list[ParsedFigure] = []
        items = exported.get("figures") or exported.get("pictures") or []
        for item in items:
            page_number = cls._page_number_from_item(item)
            figures.append(
                ParsedFigure(
                    caption=item.get("caption"),
                    figure_type=item.get("figure_type", "unknown"),
                    page_number=page_number,
                    bbox=cls._bbox_from_item(item, page_number),
                    image_ref=item.get("image_ref"),
                    alt_text=item.get("alt_text"),
                    confidence=cls._confidence_from_item(item),
                )
            )
        return figures

    @staticmethod
    def _confidence_from_item(item: dict[str, Any]) -> float:
        raw_value = item.get("confidence", item.get("score"))
        if raw_value is None:
            provenance = item.get("prov")
            if isinstance(provenance, list) and provenance:
                first = provenance[0]
                if isinstance(first, dict):
                    raw_value = first.get("confidence", first.get("score"))
        if raw_value is None:
            return 1.0
        return max(0.0, min(1.0, float(raw_value)))

    @staticmethod
    def _page_number_from_item(item: dict[str, Any], default: int = 1) -> int:
        direct_page_number = item.get("page_number") or item.get("page") or item.get("page_no")
        if direct_page_number is not None:
            return int(direct_page_number)

        provenance = item.get("prov")
        if isinstance(provenance, list) and provenance:
            first = provenance[0]
            if isinstance(first, dict):
                page_number = first.get("page_no") or first.get("page_number") or first.get("page")
                if page_number is not None:
                    return int(page_number)

        return default

    @classmethod
    def _bbox_from_item(cls, item: dict[str, Any], page_number: int) -> BoundingBox | None:
        raw_bbox = item.get("bbox")
        if raw_bbox is None:
            provenance = item.get("prov")
            if isinstance(provenance, list) and provenance:
                first = provenance[0]
                if isinstance(first, dict):
                    raw_bbox = first.get("bbox")
        return cls._build_bbox(raw_bbox, page_number)

    @staticmethod
    def _build_bbox(raw_bbox: dict | None, page_number: int) -> BoundingBox | None:
        if not raw_bbox:
            return None
        if {"l", "t", "r", "b"} <= raw_bbox.keys():
            x0, x1 = sorted((float(raw_bbox["l"]), float(raw_bbox["r"])))
            y0, y1 = sorted((float(raw_bbox["t"]), float(raw_bbox["b"])))
            return BoundingBox(
                page=page_number,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
            )
        x0, x1 = sorted((float(raw_bbox["x0"]), float(raw_bbox["x1"])))
        y0, y1 = sorted((float(raw_bbox["y0"]), float(raw_bbox["y1"])))
        return BoundingBox(
            page=page_number,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            page_width=raw_bbox.get("page_width"),
            page_height=raw_bbox.get("page_height"),
        )
