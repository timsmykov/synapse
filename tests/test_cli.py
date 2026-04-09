from __future__ import annotations

import unittest
from unittest.mock import patch

import synapse.cli as cli
from synapse.domain import TaskReceipt
from synapse.runtime_health import RuntimeHealthCheck
from synapse.services.reporting import DoctorReport
from typer.testing import CliRunner


RUNNER = CliRunner()


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

    def test_ingest_help_exposes_stable_source_output_options(self) -> None:
        result = RUNNER.invoke(cli.app, ["ingest", "--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("--source", result.stdout)
        self.assertIn("--output", result.stdout)

    def test_ingest_cli_accepts_source_and_output_options(self) -> None:
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
        ) as ingest_mock:
            result = RUNNER.invoke(
                cli.app,
                ["ingest", "--source", "paper.pdf", "--output", "data/ingest"],
            )

        self.assertEqual(result.exit_code, 0)
        self.assertIn('"command": "ingest"', result.stdout)
        ingest_mock.assert_called_once()

    def test_doctor_payload_is_serializable(self) -> None:
        with patch.object(
            cli,
            "doctor_workflow",
            return_value=DoctorReport(
                status="warn",
                app_name="Synapse",
                environment="staging",
                version="0.1.0",
                deployment_target="staging",
                public_base_url="https://synapse.example.com",
                reverse_proxy="caddy",
                data_dir="data",
                corpus_dir="test_corpus",
                eval_dir="eval",
                database_url="postgresql://postgres:5432/synapse",
                redis_url="redis://redis:6379/0",
                minio_endpoint="minio:9000",
                minio_bucket="synapse-artifacts",
                grobid_url="http://grobid:8070",
                llm_provider="openai",
                default_parser="docling",
                default_embedding_model="specter2",
                ingest_concurrency=2,
                service_endpoints={
                    "database_url": "postgresql://postgres:5432/synapse",
                    "redis_url": "redis://redis:6379/0",
                },
                warnings=["reverse proxy missing hardening"],
                checks=[
                    RuntimeHealthCheck(
                        name="reverse_proxy",
                        status="warn",
                        detail="reverse proxy needs HTTPS hardening",
                    )
                ],
            ),
        ):
            doctor_payload = cli.doctor()

        self.assertEqual(doctor_payload["command"], "doctor")
        self.assertEqual(doctor_payload["status"], "warn")
        self.assertEqual(doctor_payload["deployment_target"], "staging")
        self.assertEqual(doctor_payload["checks"][0]["name"], "reverse_proxy")


if __name__ == "__main__":
    unittest.main()
