from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from synapse.ingest.docling_adapter import DoclingAdapter, DoclingDependencyError


class _FakeDocument:
    def export_to_dict(self) -> dict:
        return {
            "title": "Synthetic Paper",
            "texts": [
                {
                    "heading": "Methods",
                    "level": 1,
                    "text": "Structured section text",
                    "confidence": 0.8,
                    "prov": [
                        {
                            "page_no": 2,
                            "bbox": {"l": 1, "t": 2, "r": 10, "b": 20},
                        }
                    ],
                }
            ],
            "tables": [
                {
                    "caption": "Table 1",
                    "rows": 1,
                    "columns": 1,
                    "prov": [{"page_no": 3}],
                    "cells": [
                        {
                            "row": 1,
                            "column": 1,
                            "text": "A",
                            "confidence": 0.7,
                            "prov": [{"page_no": 3, "bbox": {"l": 2, "t": 4, "r": 8, "b": 12}}],
                        }
                    ],
                },
                {
                    "label": "table",
                    "prov": [{"page_no": 6}],
                    "data": {
                        "num_rows": 1,
                        "num_cols": 2,
                        "table_cells": [
                            {
                                "start_row_offset_idx": 0,
                                "start_col_offset_idx": 0,
                                "text": "Header",
                                "bbox": {"l": 1, "t": 1, "r": 5, "b": 3},
                            },
                            {
                                "start_row_offset_idx": 0,
                                "start_col_offset_idx": 1,
                                "text": "Value",
                                "bbox": {"l": 6, "t": 1, "r": 12, "b": 3},
                            },
                        ],
                    },
                }
            ],
            "formulas": [{"latex": "E=mc^2", "confidence": 0.6, "prov": [{"page_no": 4}]}],
            "pictures": [
                {
                    "caption": "Figure 1",
                    "figure_type": "chart",
                    "confidence": 0.5,
                    "prov": [{"page_no": 5}],
                }
            ],
        }


class _FakeResult:
    document = _FakeDocument()


class _FakeConverter:
    def __init__(self) -> None:
        self.received_source: Path | None = None

    def convert(self, source: str) -> _FakeResult:
        self.received_source = Path(source)
        return _FakeResult()


class _ModelDumpDocument:
    def model_dump(self, *, mode: str, by_alias: bool) -> dict:
        return {
            "name": "Fallback Paper",
            "markdown": "Fallback markdown section",
        }


class _ModelDumpResult:
    document = _ModelDumpDocument()


class _ModelDumpConverter:
    def convert(self, source: str) -> _ModelDumpResult:
        return _ModelDumpResult()


class _FakeInputFormat:
    PDF = "pdf"


class _FakePdfPipelineOptions:
    def __init__(self) -> None:
        self.do_ocr = True


class _FakePdfFormatOption:
    def __init__(self, *, pipeline_options: _FakePdfPipelineOptions) -> None:
        self.pipeline_options = pipeline_options


class _CapturingDocumentConverter:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs


class _CapturingDocumentConverterModule:
    def __init__(self) -> None:
        self.instance: _CapturingDocumentConverter | None = None

    def DocumentConverter(self, **kwargs) -> _CapturingDocumentConverter:
        self.instance = _CapturingDocumentConverter(**kwargs)
        return self.instance


class DoclingAdapterTest(unittest.TestCase):
    def test_missing_dependency_is_actionable(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            with patch.object(
                DoclingAdapter,
                "_import_document_converter",
                side_effect=ModuleNotFoundError("docling"),
            ):
                with self.assertRaisesRegex(
                    DoclingDependencyError,
                    "Install `synapse\\[research\\]` or run `pip install docling`",
                ):
                    DoclingAdapter().convert(handle.name)

    def test_adapter_normalizes_structural_output(self) -> None:
        converter = _FakeConverter()
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            result = DoclingAdapter(converter_factory=lambda: converter).convert(handle.name)

        self.assertEqual(result.title, "Synthetic Paper")
        self.assertEqual(result.source_uri, handle.name)
        self.assertEqual(result.sections[0].heading, "Methods")
        self.assertEqual(result.sections[0].page_number, 2)
        self.assertEqual(result.sections[0].bbox.x0, 1.0)
        self.assertEqual(result.sections[0].bbox.y0, 2.0)
        self.assertEqual(result.sections[0].bbox.y1, 20.0)
        self.assertEqual(result.sections[0].confidence, 0.8)
        self.assertIsNone(result.tables[0].confidence)
        self.assertEqual(result.tables[0].cells[0].value, "A")
        self.assertEqual(result.tables[0].cells[0].bbox.x1, 8.0)
        self.assertEqual(result.tables[0].cells[0].confidence, 0.7)
        self.assertEqual(result.tables[1].rows, 1)
        self.assertEqual(result.tables[1].columns, 2)
        self.assertEqual(result.tables[1].cells[0].row, 1)
        self.assertEqual(result.tables[1].cells[1].column, 2)
        self.assertEqual(result.tables[1].cells[1].value, "Value")
        self.assertEqual(result.formulas[0].latex, "E=mc^2")
        self.assertEqual(result.formulas[0].confidence, 0.6)
        self.assertEqual(result.figures[0].figure_type, "chart")
        self.assertEqual(result.figures[0].confidence, 0.5)
        self.assertEqual(converter.received_source, Path(handle.name))

    def test_adapter_normalizes_bottom_left_bbox_coordinates(self) -> None:
        bbox = DoclingAdapter._build_bbox(
            {"l": 36.0, "t": 108.924, "r": 218.07, "b": 68.274, "coord_origin": "BOTTOMLEFT"},
            page_number=1,
        )

        self.assertIsNotNone(bbox)
        self.assertEqual(bbox.x0, 36.0)
        self.assertEqual(bbox.x1, 218.07)
        self.assertEqual(bbox.y0, 68.274)
        self.assertEqual(bbox.y1, 108.924)

    def test_adapter_falls_back_to_model_dump_export(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            result = DoclingAdapter(converter_factory=_ModelDumpConverter).convert(handle.name)

        self.assertEqual(result.title, "Fallback Paper")
        self.assertEqual(len(result.sections), 1)
        self.assertEqual(result.sections[0].text, "Fallback markdown section")
        self.assertIsNone(result.sections[0].confidence)

    def test_adapter_disables_ocr_when_requested(self) -> None:
        converter_module = _CapturingDocumentConverterModule()

        with patch.object(
            DoclingAdapter,
            "_import_document_converter",
            return_value=converter_module,
        ), patch.object(
            DoclingAdapter,
            "_import_input_format",
            return_value=type("InputFormatModule", (), {"InputFormat": _FakeInputFormat}),
        ), patch.object(
            DoclingAdapter,
            "_import_pdf_format_option",
            return_value=type("PdfFormatModule", (), {"PdfFormatOption": _FakePdfFormatOption}),
        ), patch.object(
            DoclingAdapter,
            "_import_pdf_pipeline_options",
            return_value=type(
                "PipelineOptionsModule",
                (),
                {"PdfPipelineOptions": _FakePdfPipelineOptions},
            ),
        ):
            converter = DoclingAdapter(ocr_enabled=False)._load_converter()

        self.assertIs(converter, converter_module.instance)
        format_options = converter.kwargs["format_options"]
        self.assertIn(_FakeInputFormat.PDF, format_options)
        self.assertFalse(format_options[_FakeInputFormat.PDF].pipeline_options.do_ocr)

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            DoclingAdapter(converter_factory=_FakeConverter).convert("missing.pdf")


if __name__ == "__main__":
    unittest.main()
