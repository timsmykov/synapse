from __future__ import annotations

import unittest

import synapse.cli as cli


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
        self.assertEqual(
            cli.ingest(),
            {
                "command": "ingest",
                "source": "test_corpus",
                "output": "data/corpus.db",
                "receipt": {
                    "artifact_count": 0,
                    "document_id": None,
                    "message": "Ingest prepared for test_corpus",
                    "result": {
                        "force": False,
                        "parser": "docling",
                        "source_uri": "test_corpus",
                        "task_id": None,
                        "task_type": "ingest",
                    },
                    "status": "queued",
                    "task_id": "test_corpus",
                    "task_type": "ingest",
                },
            },
        )
        self.assertEqual(
            cli.query(prompt="find table"),
            {
                "command": "query",
                "prompt": "find table",
                "limit": 5,
                "receipt": {
                    "artifact_count": 0,
                    "document_id": None,
                    "message": "Query prepared for top_k=5",
                    "result": {
                        "document_id": None,
                        "query": "find table",
                        "task_id": None,
                        "task_type": "query",
                        "top_k": 5,
                    },
                    "status": "queued",
                    "task_id": "find table",
                    "task_type": "query",
                },
            },
        )
        self.assertEqual(
            cli.analyze(),
            {
                "command": "analyze",
                "corpus": "data/corpus.db",
                "mode": "systematic-review",
                "receipt": {
                    "artifact_count": 0,
                    "document_id": None,
                    "message": "Analyze prepared for systematic-review",
                    "result": {
                        "analysis_mode": "systematic-review",
                        "corpus_id": "data/corpus.db",
                        "task_id": None,
                        "task_type": "analyze",
                    },
                    "status": "queued",
                    "task_id": "analyze",
                    "task_type": "analyze",
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
