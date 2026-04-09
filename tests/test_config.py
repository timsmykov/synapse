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
        self.assertEqual(summary["llm_provider"], "minimax")
        self.assertEqual(summary["default_llm_model"], "MiniMax-M2.5")
        self.assertEqual(summary["default_parser"], "docling")
        self.assertEqual(summary["embedding_provider"], "openrouter")
        self.assertEqual(summary["default_embedding_model"], "operator-configured")
        self.assertEqual(summary["parser_ocr_enabled"], "false")
        self.assertEqual(summary["colpali_enabled"], "false")
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
                "SYNAPSE_LLM_PROVIDER": "minimax",
                "SYNAPSE_DEFAULT_LLM_MODEL": "MiniMax-M2.5",
                "SYNAPSE_EMBEDDING_PROVIDER": "openrouter",
                "SYNAPSE_DEFAULT_EMBEDDING_MODEL": "text-embedding-3-small",
                "SYNAPSE_PARSER_OCR_ENABLED": "true",
                "SYNAPSE_COLPALI_ENABLED": "0",
            },
            clear=False,
        ):
            settings = Settings.from_env()

        self.assertEqual(settings.deployment_target, "staging")
        self.assertEqual(settings.public_base_url, "https://synapse.example.com")
        self.assertEqual(settings.reverse_proxy, "caddy")
        self.assertEqual(settings.grobid_url, "http://grobid:8070")
        self.assertEqual(settings.ingest_concurrency, 2)
        self.assertEqual(settings.llm_provider, "minimax")
        self.assertEqual(settings.default_llm_model, "MiniMax-M2.5")
        self.assertEqual(settings.embedding_provider, "openrouter")
        self.assertEqual(settings.default_embedding_model, "text-embedding-3-small")
        self.assertTrue(settings.parser_ocr_enabled)
        self.assertFalse(settings.colpali_enabled)


if __name__ == "__main__":
    unittest.main()
