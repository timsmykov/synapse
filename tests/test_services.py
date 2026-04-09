from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from synapse.config import Settings
from synapse.domain import DocumentRecord
from synapse.domain.tasks import AnalyzeTaskRequest, IngestTaskRequest, QueryTaskRequest
from synapse.ingest import DoclingParseResult, GrobidDependencyError
from synapse.services import analyze_workflow, doctor_workflow, ingest_workflow, query_workflow
from synapse.services.workflows import build_document_record


class ServicesTest(unittest.TestCase):
    def test_query_and_analyze_emit_task_receipts(self) -> None:
        query_receipt = query_workflow(QueryTaskRequest(query="find table"))
        analyze_receipt = analyze_workflow(AnalyzeTaskRequest(corpus_id="data/corpus.db"))

        self.assertEqual(query_receipt.task_type, "query")
        self.assertEqual(query_receipt.result["top_k"], 5)

        self.assertEqual(analyze_receipt.task_type, "analyze")
        self.assertEqual(analyze_receipt.result["corpus_id"], "data/corpus.db")

    def test_doctor_report_uses_runtime_settings(self) -> None:
        report = doctor_workflow()

        self.assertEqual(report.command, "doctor")
        self.assertEqual(report.app_name, "Synapse")
        self.assertEqual(report.default_parser, "docling")
        self.assertEqual(report.deployment_target, "local")
        self.assertEqual(report.status, "ok")
        self.assertEqual(report.grobid_url, "http://localhost:8070")
        self.assertEqual(report.warnings, [])

    def test_doctor_report_matches_remote_runtime_health_policy(self) -> None:
        report = doctor_workflow(
            Settings(
                environment="staging",
                deployment_target="staging",
            )
        )

        self.assertEqual(report.status, "fail")
        self.assertEqual(report.deployment_target, "staging")
        checks = {check.name: check for check in report.checks}
        self.assertEqual(checks["database_url"].status, "fail")
        self.assertEqual(checks["public_base_url"].status, "warn")
        self.assertTrue(report.warnings)

    def test_ingest_file_writes_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "paper.pdf"
            output_path = Path(temp_dir) / "paper.json"
            source_path.write_bytes(b"%PDF-1.4\n")

            document = DocumentRecord(document_id="paper", title="Paper", artifacts=[])
            with patch(
                "synapse.services.workflows.build_document_record",
                return_value=(document, []),
            ):
                receipt = ingest_workflow(
                    IngestTaskRequest(source_uri=str(source_path), output_uri=str(output_path))
                )

        self.assertEqual(receipt.status, "succeeded")
        self.assertEqual(receipt.document_id, "paper")
        self.assertEqual(receipt.result["output_uri"], str(output_path))
        self.assertEqual(receipt.result["document_id"], "paper")
        self.assertEqual(receipt.result["written_files"], [str(output_path)])

    def test_ingest_directory_writes_batch_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "paper-a.pdf"
            second = root / "paper-b.pdf"
            output_dir = root / "ingest-json"
            first.write_bytes(b"%PDF-1.4\n")
            second.write_bytes(b"%PDF-1.4\n")

            def fake_build_document_record(source_path: Path) -> tuple[DocumentRecord, list[str]]:
                return (
                    DocumentRecord(
                        document_id=source_path.stem,
                        title=source_path.stem,
                        artifacts=[],
                    ),
                    [],
                )

            with patch(
                "synapse.services.workflows.build_document_record",
                side_effect=fake_build_document_record,
            ):
                receipt = ingest_workflow(
                    IngestTaskRequest(source_uri=str(root), output_uri=str(output_dir))
                )

        self.assertEqual(receipt.status, "succeeded")
        self.assertEqual(receipt.document_id, None)
        self.assertEqual(receipt.result["documents"], ["paper-a", "paper-b"])
        self.assertEqual(
            receipt.result["written_files"],
            [str(output_dir / "paper-a.json"), str(output_dir / "paper-b.json")],
        )

    def test_ingest_missing_source_stays_queued(self) -> None:
        receipt = ingest_workflow(IngestTaskRequest(source_uri="test_corpus"))

        self.assertEqual(receipt.status, "failed")
        self.assertEqual(receipt.task_id, "test_corpus")
        self.assertEqual(receipt.result["source_uri"], "test_corpus")
        self.assertIn("error", receipt.result)

    def test_build_document_record_falls_back_when_grobid_is_missing(self) -> None:
        structure = DoclingParseResult(
            document_id="paper",
            title="Paper",
            source_uri="/tmp/paper.pdf",
        )
        document = DocumentRecord(
            document_id="paper",
            title="Paper",
            source_uri="/tmp/paper.pdf",
            artifacts=[],
        )

        with (
            patch("synapse.services.workflows.DoclingAdapter.convert", return_value=structure),
            patch(
                "synapse.services.workflows.GrobidAdapter.extract",
                side_effect=GrobidDependencyError("grobid unavailable"),
            ),
            patch(
                "synapse.services.workflows.merge_document_record",
                return_value=document,
            ) as merge_mock,
        ):
            result, warnings = build_document_record(Path("/tmp/paper.pdf"))

        self.assertIs(result, document)
        self.assertEqual(warnings, ["grobid unavailable"])
        merge_mock.assert_called_once_with(structure, None)

    def test_build_document_record_passes_ocr_setting_to_docling(self) -> None:
        structure = DoclingParseResult(
            document_id="paper",
            title="Paper",
            source_uri="/tmp/paper.pdf",
        )
        document = DocumentRecord(
            document_id="paper",
            title="Paper",
            source_uri="/tmp/paper.pdf",
            artifacts=[],
        )

        with (
            patch(
                "synapse.services.workflows.get_settings",
                return_value=Settings(parser_ocr_enabled=False),
            ),
            patch("synapse.services.workflows.DoclingAdapter") as docling_adapter_cls,
            patch("synapse.services.workflows.GrobidAdapter.extract", return_value=None),
            patch(
                "synapse.services.workflows.merge_document_record",
                return_value=document,
            ),
        ):
            docling_adapter_cls.return_value.convert.return_value = structure

            result, warnings = build_document_record(Path("/tmp/paper.pdf"))

        self.assertIs(result, document)
        self.assertEqual(warnings, [])
        docling_adapter_cls.assert_called_once_with(ocr_enabled=False)
        docling_adapter_cls.return_value.convert.assert_called_once_with("/tmp/paper.pdf")

    def test_build_document_record_falls_back_when_grobid_runtime_fails(self) -> None:
        structure = DoclingParseResult(
            document_id="paper",
            title="Paper",
            source_uri="/tmp/paper.pdf",
        )
        document = DocumentRecord(
            document_id="paper",
            title="Paper",
            source_uri="/tmp/paper.pdf",
            artifacts=[],
        )

        with (
            patch("synapse.services.workflows.DoclingAdapter.convert", return_value=structure),
            patch(
                "synapse.services.workflows.GrobidAdapter.extract",
                side_effect=RuntimeError("connection refused"),
            ),
            patch(
                "synapse.services.workflows.merge_document_record",
                return_value=document,
            ) as merge_mock,
        ):
            result, warnings = build_document_record(Path("/tmp/paper.pdf"))

        self.assertIs(result, document)
        self.assertEqual(len(warnings), 1)
        self.assertIn("GROBID extraction failed for paper.pdf", warnings[0])
        self.assertIn("connection refused", warnings[0])
        merge_mock.assert_called_once_with(structure, None)


if __name__ == "__main__":
    unittest.main()
