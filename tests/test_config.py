from __future__ import annotations

import unittest

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

    def test_get_settings_is_cached(self) -> None:
        first = get_settings()
        second = get_settings()

        self.assertIs(first, second)


if __name__ == "__main__":
    unittest.main()
