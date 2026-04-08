from __future__ import annotations

import unittest
from unittest.mock import patch

import synapse.cli as cli
from synapse.domain import TaskReceipt


class CliTest(unittest.TestCase):
    def test_commands_are_registered(self) -> None:
        if hasattr(cli.app, "registered_commands"):
            commands = {command.name for command in cli.app.registered_commands}
        else:
            commands = set(getattr(cli.app, "commands", {}))

        self.assertIn("ingest", commands)
        self.assertIn("query", commands)
        self.assertIn("analyze", commands)
        self.assertIn("doctor", commands)

    def test_command_payloads_are_serializable(self) -> None:
        with patch.object(
            cli,
            "ingest_workflow",
            return_value=TaskReceipt(
                task_id="paper.pdf",
                task_type="ingest",
                status="succeeded",
                message="Ingested 1 document(s) to data/ingest",
                document_id="paper",
                artifact_count=1,
                result={
                    "source_uri": "paper.pdf",
                    "output_uri": "data/ingest",
                    "parser": "docling",
                    "document_id": "paper",
                    "documents": ["paper"],
                    "artifact_count": 1,
                    "resolved_sources": ["paper.pdf"],
                    "written_files": ["data/ingest/paper.json"],
                    "warnings": [],
                },
            ),
        ):
            ingest_payload = cli.ingest(source="paper.pdf")
        query_payload = cli.query(prompt="find table")
        analyze_payload = cli.analyze()

        self.assertEqual(ingest_payload["command"], "ingest")
        self.assertEqual(ingest_payload["source"], "paper.pdf")
        self.assertEqual(ingest_payload["output"], "data/ingest")
        self.assertEqual(ingest_payload["receipt"]["result"]["output_uri"], "data/ingest")

        self.assertEqual(query_payload["command"], "query")
        self.assertEqual(query_payload["receipt"]["result"]["query"], "find table")
        self.assertEqual(query_payload["receipt"]["result"]["top_k"], 5)

        self.assertEqual(analyze_payload["command"], "analyze")
        self.assertEqual(analyze_payload["receipt"]["result"]["corpus_id"], "data/corpus.db")
        self.assertEqual(analyze_payload["receipt"]["result"]["analysis_mode"], "systematic-review")


if __name__ == "__main__":
    unittest.main()
