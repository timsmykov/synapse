from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from synapse.domain import DocumentRecord, Provenance, Section
from synapse.ingest.io import resolve_ingest_sources, write_document_records


def _record(document_id: str = "paper") -> DocumentRecord:
    provenance = Provenance(source_document_id=document_id, page_number=1, parser="docling")
    return DocumentRecord(
        document_id=document_id,
        title=f"Title for {document_id}",
        source_uri=f"/tmp/{document_id}.pdf",
        provenance=provenance,
        artifacts=[
            Section(
                artifact_id=f"{document_id}:section:1",
                document_id=document_id,
                provenance=provenance,
                heading="Intro",
                level=1,
                text="Body",
            )
        ],
    )


class ResolveIngestSourcesTest(unittest.TestCase):
    def test_resolves_single_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf = Path(tmpdir) / "paper.pdf"
            pdf.write_bytes(b"%PDF")

            self.assertEqual(resolve_ingest_sources(str(pdf)), [pdf])

    def test_resolves_directory_recursively(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            nested = root / "nested"
            nested.mkdir()
            first = root / "a.pdf"
            second = nested / "b.pdf"
            first.write_bytes(b"%PDF")
            second.write_bytes(b"%PDF")

            self.assertEqual(resolve_ingest_sources(str(root)), [first, second])

    def test_resolves_glob_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            first = root / "a.pdf"
            second = root / "b.pdf"
            first.write_bytes(b"%PDF")
            second.write_bytes(b"%PDF")

            self.assertEqual(
                resolve_ingest_sources(str(root / "*.pdf")),
                [first, second],
            )

    def test_rejects_non_pdf_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            text_file = Path(tmpdir) / "notes.txt"
            text_file.write_text("hello", encoding="utf-8")

            with self.assertRaises(ValueError):
                resolve_ingest_sources(str(text_file))


class WriteDocumentRecordsTest(unittest.TestCase):
    def test_writes_single_record_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "paper.json"

            written = write_document_records([_record()], output)

            self.assertEqual(written, [output])
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["document_id"], "paper")

    def test_writes_batch_to_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "json"

            written = write_document_records([_record("paper-1"), _record("paper-2")], output)

            self.assertEqual(written, [output / "paper-1.json", output / "paper-2.json"])
            self.assertTrue((output / "paper-1.json").exists())
            self.assertTrue((output / "paper-2.json").exists())

    def test_rejects_batch_output_to_single_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "batch.json"

            with self.assertRaises(ValueError):
                write_document_records([_record("paper-1"), _record("paper-2")], output)


if __name__ == "__main__":
    unittest.main()
