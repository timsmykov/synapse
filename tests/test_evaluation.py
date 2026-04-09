from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from synapse.domain import (
    BoundingBox,
    Citation,
    DocumentRecord,
    FormulaArtifact,
    Provenance,
    Section,
    TableArtifact,
    TableCell,
)
from synapse.evaluation import (
    audit_corpus_manifest,
    evaluate_document_record,
    evaluate_ingest_outputs,
    load_corpus_manifest,
)


class EvaluationTest(unittest.TestCase):
    def test_load_corpus_manifest_validates_supported_layout_features(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    [
                        {
                            "document_id": "doc-01",
                            "file_name": "01-ecommerce-meta-analysis.pdf",
                            "domain": "medicine",
                            "source_path": "/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf",
                            "layout_features": ["tables", "figures"],
                            "expected_artifacts": {
                                "sections": 2,
                                "tables": 1,
                                "table_cells": 2,
                                "formulas": 1,
                                "figures": 1,
                                "citations": 0,
                            },
                            "notes": "fixture",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            entries = load_corpus_manifest(manifest_path)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].file_name, "01-ecommerce-meta-analysis.pdf")
        self.assertEqual(
            entries[0].source_path,
            "/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf",
        )

    def test_evaluate_document_record_reports_green_metrics_for_matching_counts(self) -> None:
        entry = load_corpus_manifest_data()[0]
        provenance = Provenance(
            source_document_id="doc-01",
            page_number=1,
            parser="docling",
            confidence=1.0,
            bbox=BoundingBox(page=1, x0=0.0, y0=0.0, x1=10.0, y1=10.0),
            citation=Citation(title="Study"),
        )
        document = DocumentRecord(
            document_id="doc-01",
            title="Study",
            artifacts=[
                Section(
                    artifact_id="sec-1",
                    document_id="doc-01",
                    provenance=provenance,
                    heading="Intro",
                    level=1,
                    text="A",
                    order=0,
                ),
                Section(
                    artifact_id="sec-2",
                    document_id="doc-01",
                    provenance=provenance,
                    heading="Methods",
                    level=1,
                    text="B",
                    order=1,
                ),
                TableArtifact(
                    artifact_id="tbl-1",
                    document_id="doc-01",
                    provenance=provenance,
                    rows=1,
                    columns=2,
                    cells=[
                        TableCell(
                            artifact_id="cell-1",
                            document_id="doc-01",
                            provenance=provenance,
                            row=1,
                            column=1,
                        ),
                        TableCell(
                            artifact_id="cell-2",
                            document_id="doc-01",
                            provenance=provenance,
                            row=1,
                            column=2,
                        ),
                    ],
                ),
                FormulaArtifact(
                    artifact_id="form-1",
                    document_id="doc-01",
                    provenance=provenance,
                    latex="E=mc^2",
                ),
            ],
        )

        report = evaluate_document_record(document, entry)
        metrics = {metric.name: metric for metric in report.metrics}

        self.assertTrue(report.passed)
        self.assertEqual(metrics["table_extraction_accuracy"].value, 1.0)
        self.assertEqual(metrics["formula_fidelity"].value, 1.0)
        self.assertEqual(metrics["provenance_correctness"].value, 1.0)
        self.assertEqual(metrics["section_order_correctness"].value, 1.0)

    def test_evaluate_ingest_outputs_requires_manifest_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "manifest.json"
            output_path = root / "doc.json"
            manifest_path.write_text(
                json.dumps(
                    [
                        {
                            "document_id": "doc-01",
                            "file_name": "01-ecommerce-meta-analysis.pdf",
                            "domain": "medicine",
                            "layout_features": ["tables"],
                            "expected_artifacts": {
                                "sections": 0,
                                "tables": 0,
                                "table_cells": 0,
                                "formulas": 0,
                                "figures": 0,
                                "citations": 0,
                            },
                            "notes": "fixture",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output_path.write_text(
                DocumentRecord(document_id="doc-02", title="Other").model_dump_json(),
                encoding="utf-8",
            )

            with self.assertRaises(KeyError):
                evaluate_ingest_outputs(manifest_path, output_path)

    def test_evaluate_ingest_outputs_matches_by_fixture_file_stem(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "manifest.json"
            output_path = root / "01-ecommerce-meta-analysis.json"
            manifest_path.write_text(
                json.dumps(
                    [
                        {
                            "document_id": "doc-01",
                            "file_name": "01-ecommerce-meta-analysis.pdf",
                            "domain": "ecommerce",
                            "source_path": "/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf",
                            "layout_features": ["tables"],
                            "expected_artifacts": {
                                "sections": 0,
                                "tables": 0,
                                "table_cells": 0,
                                "formulas": 0,
                                "figures": 0,
                                "citations": 0,
                            },
                            "notes": "fixture",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output_path.write_text(
                DocumentRecord(document_id="01-ecommerce-meta-analysis", title="Study").model_dump_json(),
                encoding="utf-8",
            )

            reports = evaluate_ingest_outputs(manifest_path, output_path)

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].fixture_file_name, "01-ecommerce-meta-analysis.pdf")

    def test_evaluate_ingest_outputs_can_require_full_fixture_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "manifest.json"
            output_path = root / "01-ecommerce-meta-analysis.json"
            manifest_path.write_text(
                json.dumps(
                    [
                        {
                            "document_id": "doc-01",
                            "file_name": "01-ecommerce-meta-analysis.pdf",
                            "domain": "ecommerce",
                            "layout_features": ["tables"],
                            "expected_artifacts": {
                                "sections": 0,
                                "tables": 0,
                                "table_cells": 0,
                                "formulas": 0,
                                "figures": 0,
                                "citations": 0,
                            },
                            "notes": "fixture",
                        },
                        {
                            "document_id": "doc-02",
                            "file_name": "02-service-robot-study.pdf",
                            "domain": "robots",
                            "layout_features": ["tables"],
                            "expected_artifacts": {
                                "sections": 0,
                                "tables": 0,
                                "table_cells": 0,
                                "formulas": 0,
                                "figures": 0,
                                "citations": 0,
                            },
                            "notes": "fixture",
                        },
                    ]
                ),
                encoding="utf-8",
            )
            output_path.write_text(
                DocumentRecord(document_id="01-ecommerce-meta-analysis", title="Study").model_dump_json(),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "full golden corpus fixture set"):
                evaluate_ingest_outputs(
                    manifest_path,
                    output_path,
                    require_complete_fixture_set=True,
                )

    def test_audit_corpus_manifest_reports_missing_and_undocumented_files(self) -> None:
        fixtures = load_corpus_manifest_data()
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus_dir = Path(temp_dir)
            (corpus_dir / "extra.pdf").write_bytes(b"%PDF-1.4\n")
            audit = audit_corpus_manifest(
                fixtures,
                manifest_path="test_corpus/corpus-manifest.json",
                corpus_dir=corpus_dir,
            )

        self.assertEqual(audit.status, "fail")
        self.assertIn("01-ecommerce-meta-analysis.pdf", audit.missing_files)
        self.assertIn("extra.pdf", audit.undocumented_files)

    def test_minimum_expectations_allow_actual_counts_above_manifest_floor(self) -> None:
        entry = load_corpus_manifest_from_json(
            [
                {
                    "document_id": "doc-01",
                    "file_name": "01-ecommerce-meta-analysis.pdf",
                    "domain": "ecommerce",
                    "layout_features": ["tables"],
                    "expected_artifacts": {
                        "sections": 1,
                        "tables": 1,
                        "table_cells": 1,
                        "formulas": 0,
                        "figures": 0,
                        "citations": 0,
                    },
                    "notes": "fixture",
                }
            ]
        )[0]
        provenance = Provenance(
            source_document_id="doc-01",
            page_number=1,
            parser="docling",
            confidence=1.0,
        )
        document = DocumentRecord(
            document_id="doc-01",
            title="Study",
            artifacts=[
                Section(
                    artifact_id="sec-1",
                    document_id="doc-01",
                    provenance=provenance,
                    heading="Intro",
                    level=1,
                    text="A",
                    order=0,
                ),
                TableArtifact(
                    artifact_id="tbl-1",
                    document_id="doc-01",
                    provenance=provenance,
                    rows=1,
                    columns=2,
                    cells=[
                        TableCell(
                            artifact_id="cell-1",
                            document_id="doc-01",
                            provenance=provenance,
                            row=1,
                            column=1,
                        ),
                        TableCell(
                            artifact_id="cell-2",
                            document_id="doc-01",
                            provenance=provenance,
                            row=1,
                            column=2,
                        ),
                    ],
                ),
            ],
        )

        report = evaluate_document_record(document, entry)
        metrics = {metric.name: metric for metric in report.metrics}

        self.assertEqual(metrics["table_extraction_accuracy"].value, 1.0)

    def test_provenance_metric_allows_missing_confidence_when_other_fields_are_valid(self) -> None:
        entry = load_corpus_manifest_data()[0]
        provenance = Provenance(
            source_document_id="doc-01",
            page_number=1,
            parser="docling",
        )
        document = DocumentRecord(
            document_id="doc-01",
            title="Study",
            artifacts=[
                Section(
                    artifact_id="sec-1",
                    document_id="doc-01",
                    provenance=provenance,
                    heading="Intro",
                    level=1,
                    text="A",
                    order=0,
                )
            ],
        )

        report = evaluate_document_record(document, entry)
        metrics = {metric.name: metric for metric in report.metrics}

        self.assertEqual(metrics["provenance_correctness"].value, 1.0)


def load_corpus_manifest_data() -> list:
    return load_corpus_manifest_from_json(
        [
            {
                "document_id": "doc-01",
                "file_name": "01-ecommerce-meta-analysis.pdf",
                "domain": "medicine",
                "source_path": "/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf",
                "layout_features": ["tables", "formulas", "multi_column"],
                "expected_artifacts": {
                    "sections": 2,
                    "tables": 1,
                    "table_cells": 2,
                    "formulas": 1,
                    "figures": 0,
                    "citations": 0,
                },
                "notes": "fixture",
            }
        ]
    )


def load_corpus_manifest_from_json(payload: list[dict]) -> list:
    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_path = Path(temp_dir) / "manifest.json"
        manifest_path.write_text(json.dumps(payload), encoding="utf-8")
        return load_corpus_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
