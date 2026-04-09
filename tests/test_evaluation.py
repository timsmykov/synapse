from __future__ import annotations

import json
import os
import subprocess
import sys
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
    IngestCoverageError,
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

    def test_evaluate_ingest_outputs_requires_full_manifest_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "manifest.json"
            outputs_dir = root / "outputs"
            outputs_dir.mkdir()
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
                        },
                        {
                            "document_id": "doc-02",
                            "file_name": "02-jams-service-review.pdf",
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
                        },
                    ]
                ),
                encoding="utf-8",
            )
            (outputs_dir / "doc-01.json").write_text(
                DocumentRecord(document_id="doc-01", title="Study").model_dump_json(),
                encoding="utf-8",
            )

            with self.assertRaises(IngestCoverageError) as context:
                evaluate_ingest_outputs(manifest_path, outputs_dir)

        self.assertEqual(context.exception.manifest_path, str(manifest_path))
        self.assertEqual(context.exception.output_path, str(outputs_dir))
        self.assertEqual(context.exception.evaluated_document_ids, ["doc-01"])
        self.assertEqual(context.exception.missing_document_ids, ["doc-02"])

    def test_evaluate_ingest_script_reports_manifest_and_missing_document_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "manifest.json"
            outputs_dir = root / "outputs"
            outputs_dir.mkdir()
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
                        },
                        {
                            "document_id": "doc-02",
                            "file_name": "02-jams-service-review.pdf",
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
                        },
                    ]
                ),
                encoding="utf-8",
            )
            (outputs_dir / "doc-01.json").write_text(
                DocumentRecord(document_id="doc-01", title="Study").model_dump_json(),
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/evaluate_ingest.py",
                    str(outputs_dir),
                    "--manifest",
                    str(manifest_path),
                ],
                check=False,
                capture_output=True,
                cwd=Path(__file__).resolve().parents[1],
                env=env,
                text=True,
            )

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["passed"])
        self.assertEqual(payload["manifest_path"], str(manifest_path))
        self.assertEqual(payload["ingest_output"], str(outputs_dir))
        self.assertEqual(payload["evaluated_document_ids"], ["doc-01"])
        self.assertEqual(payload["missing_document_ids"], ["doc-02"])
        self.assertIn("missing document_ids: doc-02", payload["error"])

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


def load_corpus_manifest_data() -> list:
    return load_corpus_manifest_from_json(
        [
            {
                "document_id": "doc-01",
                "file_name": "01-ecommerce-meta-analysis.pdf",
                "domain": "medicine",
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
