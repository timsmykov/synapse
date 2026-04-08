from __future__ import annotations

import unittest

from synapse.domain import (
    AnalyzeTaskRequest,
    BoundingBox,
    Citation,
    DocumentRecord,
    FigureArtifact,
    FormulaArtifact,
    IngestTaskRequest,
    Provenance,
    QueryTaskRequest,
    Section,
    TableArtifact,
    TableCell,
    TaskReceipt,
)


class DomainContractsTest(unittest.TestCase):
    def test_bounding_box_accepts_alias_and_serializes(self) -> None:
        bbox = BoundingBox(page=3, x0=1.0, y0=2.0, x1=10.0, y1=20.0)

        self.assertEqual(bbox.page_number, 3)
        self.assertEqual(bbox.model_dump(mode="json")["page_number"], 3)

    def test_provenance_serializes_with_bbox_and_citation(self) -> None:
        provenance = Provenance(
            source_document_id="doc-1",
            page_number=3,
            bbox=BoundingBox(page=3, x0=1.0, y0=2.0, x1=10.0, y1=20.0),
            confidence=0.93,
            parser="docling",
            citation=Citation(
                title="Example Trial",
                authors=["Doe, J."],
                year=2024,
                doi="10.1000/example",
            ),
        )

        payload = provenance.model_dump(mode="json")

        self.assertEqual(payload["source_document_id"], "doc-1")
        self.assertEqual(payload["bbox"]["page_number"], 3)
        self.assertEqual(payload["citation"]["doi"], "10.1000/example")

    def test_document_record_round_trips_artifact_union(self) -> None:
        provenance = Provenance(source_document_id="doc-1", page_number=1, parser="docling")
        record = DocumentRecord(
            document_id="doc-1",
            title="Example Study",
            source_uri="file:///tmp/example.pdf",
            authors=["Doe, J."],
            provenance=provenance,
            citation=Citation(title="Example Study", authors=["Doe, J."], year=2024),
            artifacts=[
                Section(
                    artifact_id="sec-1",
                    document_id="doc-1",
                    provenance=provenance,
                    heading="Introduction",
                    level=1,
                    text="Background text.",
                ),
                TableArtifact(
                    artifact_id="tbl-1",
                    document_id="doc-1",
                    provenance=Provenance(source_document_id="doc-1", page_number=2),
                    rows=1,
                    columns=1,
                    cells=[
                        TableCell(
                            artifact_id="cell-1",
                            document_id="doc-1",
                            provenance=Provenance(source_document_id="doc-1", page_number=2),
                            row=1,
                            column=1,
                            normalized_value=42,
                        )
                    ],
                ),
                FormulaArtifact(
                    artifact_id="form-1",
                    document_id="doc-1",
                    provenance=Provenance(source_document_id="doc-1", page_number=4),
                    latex="x = y + z",
                    display_mode=True,
                ),
                FigureArtifact(
                    artifact_id="fig-1",
                    document_id="doc-1",
                    provenance=Provenance(source_document_id="doc-1", page_number=5),
                    caption="Outcome curve",
                    figure_type="plot",
                ),
            ],
        )

        restored = DocumentRecord.model_validate_json(record.model_dump_json())

        self.assertEqual(restored.document_id, "doc-1")
        self.assertEqual(restored.provenance.source_document_id, "doc-1")
        self.assertEqual(len(restored.artifacts), 4)
        self.assertIsInstance(restored.artifacts[0], Section)
        self.assertIsInstance(restored.artifacts[1], TableArtifact)
        self.assertIsInstance(restored.artifacts[2], FormulaArtifact)
        self.assertIsInstance(restored.artifacts[3], FigureArtifact)

    def test_provenance_rejects_mismatched_bbox_page(self) -> None:
        with self.assertRaises(ValueError):
            Provenance(
                source_document_id="doc-1",
                page_number=1,
                bbox=BoundingBox(page=2, x0=1.0, y0=1.0, x1=2.0, y1=2.0),
            )

    def test_document_record_rejects_mismatched_provenance(self) -> None:
        with self.assertRaises(ValueError):
            DocumentRecord(
                document_id="doc-1",
                title="Example Study",
                provenance=Provenance(source_document_id="doc-2", page_number=1),
            )

    def test_table_requires_cells_within_bounds(self) -> None:
        with self.assertRaises(ValueError):
            TableArtifact(
                artifact_id="tbl-1",
                document_id="doc-1",
                provenance=Provenance(source_document_id="doc-1", page_number=2),
                rows=1,
                columns=1,
                cells=[
                    TableCell(
                        artifact_id="cell-1",
                        document_id="doc-1",
                        provenance=Provenance(source_document_id="doc-1", page_number=2),
                        row=2,
                        column=1,
                    )
                ],
            )

    def test_task_models_are_serializable(self) -> None:
        ingest = IngestTaskRequest(source_uri="file:///tmp/example.pdf")
        query = QueryTaskRequest(query="table 2")
        analyze = AnalyzeTaskRequest(corpus_id="corpus-1")
        receipt = TaskReceipt(task_id="task-1", task_type="ingest", document_id="doc-1")

        self.assertEqual(ingest.model_dump(mode="json")["task_type"], "ingest")
        self.assertEqual(query.model_dump(mode="json")["top_k"], 5)
        self.assertEqual(analyze.model_dump(mode="json")["analysis_mode"], "systematic-review")
        self.assertEqual(receipt.status, "queued")


if __name__ == "__main__":
    unittest.main()

