from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from synapse.config import Settings, get_settings


class SettingsTest(unittest.TestCase):
    def test_settings_summary_contains_expected_fields(self) -> None:
        settings = Settings()
        summary = settings.summary

        self.assertEqual(summary["app_name"], "Synapse")
        self.assertEqual(summary["environment"], "development")
        self.assertEqual(summary["version"], "0.1.0")
        self.assertEqual(summary["default_parser"], "docling")
        self.assertEqual(summary["minio_bucket"], "synapse-artifacts")
        self.assertEqual(summary["deployment_target"], "local")
        self.assertEqual(summary["reverse_proxy"], "none")
        self.assertEqual(summary["grobid_url"], "http://localhost:8070")
        self.assertEqual(summary["ingest_concurrency"], "1")

    def test_get_settings_is_cached(self) -> None:
        first = get_settings()
        second = get_settings()

        self.assertIs(first, second)

    def test_settings_from_env_reads_server_runtime_fields(self) -> None:
        with patch.dict(
            os.environ,
            {
                "SYNAPSE_DEPLOYMENT_TARGET": "staging",
                "SYNAPSE_PUBLIC_BASE_URL": "https://synapse.example.com",
                "SYNAPSE_REVERSE_PROXY": "caddy",
                "SYNAPSE_GROBID_URL": "http://grobid:8070",
                "SYNAPSE_INGEST_CONCURRENCY": "2",
            },
            clear=False,
        ):
            settings = Settings.from_env()

        self.assertEqual(settings.deployment_target, "staging")
        self.assertEqual(settings.public_base_url, "https://synapse.example.com")
        self.assertEqual(settings.reverse_proxy, "caddy")
        self.assertEqual(settings.grobid_url, "http://grobid:8070")
        self.assertEqual(settings.ingest_concurrency, 2)


if __name__ == "__main__":
    unittest.main()
