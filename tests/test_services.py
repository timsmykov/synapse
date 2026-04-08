from __future__ import annotations

import unittest

from synapse.domain.tasks import AnalyzeTaskRequest, IngestTaskRequest, QueryTaskRequest
from synapse.services import analyze_workflow, doctor_workflow, ingest_workflow, query_workflow


class ServicesTest(unittest.TestCase):
    def test_ingest_query_and_analyze_emit_task_receipts(self) -> None:
        ingest_receipt = ingest_workflow(IngestTaskRequest(source_uri="test_corpus"))
        query_receipt = query_workflow(QueryTaskRequest(query="find table"))
        analyze_receipt = analyze_workflow(AnalyzeTaskRequest(corpus_id="data/corpus.db"))

        self.assertEqual(ingest_receipt.task_type, "ingest")
        self.assertEqual(ingest_receipt.task_id, "test_corpus")
        self.assertEqual(ingest_receipt.result["parser"], "docling")

        self.assertEqual(query_receipt.task_type, "query")
        self.assertEqual(query_receipt.result["top_k"], 5)

        self.assertEqual(analyze_receipt.task_type, "analyze")
        self.assertEqual(analyze_receipt.result["corpus_id"], "data/corpus.db")

    def test_doctor_report_uses_runtime_settings(self) -> None:
        report = doctor_workflow()

        self.assertEqual(report.command, "doctor")
        self.assertEqual(report.app_name, "Synapse")
        self.assertEqual(report.default_parser, "docling")


if __name__ == "__main__":
    unittest.main()

