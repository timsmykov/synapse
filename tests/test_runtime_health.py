from __future__ import annotations

import unittest

from synapse.config import Settings
from synapse.runtime_health import build_runtime_health_report


class RuntimeHealthReportTest(unittest.TestCase):
    def test_local_defaults_are_ok_for_local_target(self) -> None:
        report = build_runtime_health_report(Settings())

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.deployment_target, "local")
        self.assertEqual(report.warnings, [])
        checks = {item.name: item for item in report.checks}
        self.assertEqual(checks["database_url"].status, "ok")
        self.assertEqual(checks["ingest_concurrency"].status, "ok")

    def test_staging_requires_server_friendly_endpoints(self) -> None:
        report = build_runtime_health_report(
            Settings(
                environment="staging",
                deployment_target="staging",
            )
        )

        self.assertEqual(report.status, "fail")
        checks = {item.name: item for item in report.checks}
        self.assertEqual(checks["database_url"].status, "fail")
        self.assertEqual(checks["redis_url"].status, "fail")
        self.assertEqual(checks["minio_endpoint"].status, "fail")
        self.assertEqual(checks["grobid_url"].status, "fail")
        self.assertEqual(checks["public_base_url"].status, "warn")
        self.assertEqual(checks["reverse_proxy"].status, "warn")

    def test_staging_can_be_clean_when_internal_services_are_named(self) -> None:
        report = build_runtime_health_report(
            Settings(
                environment="staging",
                deployment_target="staging",
                public_base_url="https://synapse.example.com",
                reverse_proxy="caddy",
                database_url="postgresql+psycopg://synapse:synapse@postgres:5432/synapse",
                redis_url="redis://redis:6379/0",
                minio_endpoint="minio:9000",
                grobid_url="http://grobid:8070",
                llm_provider="openai",
            )
        )

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.warnings, [])

    def test_staging_warns_when_concurrency_is_aggressive(self) -> None:
        report = build_runtime_health_report(
            Settings(
                environment="staging",
                deployment_target="staging",
                public_base_url="https://synapse.example.com",
                reverse_proxy="caddy",
                database_url="postgresql+psycopg://synapse:synapse@postgres:5432/synapse",
                redis_url="redis://redis:6379/0",
                minio_endpoint="minio:9000",
                grobid_url="http://grobid:8070",
                llm_provider="openai",
                ingest_concurrency=4,
            )
        )

        self.assertEqual(report.status, "warn")
        checks = {item.name: item for item in report.checks}
        self.assertEqual(checks["ingest_concurrency"].status, "warn")

    def test_testing_target_uses_remote_server_checks(self) -> None:
        report = build_runtime_health_report(
            Settings(
                environment="testing",
                deployment_target="testing",
            )
        )

        self.assertEqual(report.status, "fail")
        checks = {item.name: item for item in report.checks}
        self.assertEqual(checks["database_url"].status, "fail")
        self.assertEqual(checks["redis_url"].status, "fail")
        self.assertEqual(checks["minio_endpoint"].status, "fail")
        self.assertEqual(checks["grobid_url"].status, "fail")
        self.assertEqual(checks["public_base_url"].status, "warn")
        self.assertEqual(checks["reverse_proxy"].status, "warn")


if __name__ == "__main__":
    unittest.main()
