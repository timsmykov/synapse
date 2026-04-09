from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from synapse.ingest.grobid_adapter import (
    GrobidAdapter,
    GrobidDependencyError,
)

TEI_XML = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>Example GROBID Title</title>
      </titleStmt>
      <publicationStmt>
        <date when="2024-01-01">2024</date>
        <idno type="DOI">10.1000/example</idno>
      </publicationStmt>
      <sourceDesc>
        <biblStruct>
          <analytic>
            <author><persName><forename>Ada</forename><surname>Lovelace</surname></persName></author>
          </analytic>
        </biblStruct>
      </sourceDesc>
    </fileDesc>
    <profileDesc>
      <abstract><p>Structured abstract.</p></abstract>
    </profileDesc>
  </teiHeader>
</TEI>
"""


class _ModernFakeClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def process(self, **kwargs: object) -> None:
        self.calls.append(kwargs)
        input_dir = Path(str(kwargs["input_path"]))
        self._assert_staged_single_pdf(input_dir)

        output_dir = Path(str(kwargs["output_path"]))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "document.grobid.tei.xml"
        output_path.write_text(TEI_XML, encoding="utf-8")

    @staticmethod
    def _assert_staged_single_pdf(input_dir: Path) -> None:
        pdf_files = list(input_dir.glob("*.pdf"))
        if len(pdf_files) != 1:
            raise AssertionError("expected exactly one staged PDF in input_path")


class _LegacyFakeClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def process(self, **kwargs: object) -> None:
        self.calls.append(kwargs)
        if "output_path" in kwargs or "teiCoordinates" in kwargs:
            raise TypeError("legacy client does not support modern keyword names")

        input_dir = Path(str(kwargs["input_path"]))
        _ModernFakeClient._assert_staged_single_pdf(input_dir)

        output_dir = Path(str(kwargs["output"]))
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "document.tei.xml"
        output_path.write_text(TEI_XML, encoding="utf-8")


class _UnavailableFakeClient:
    def process(self, **kwargs: object) -> None:
        raise RuntimeError("server unavailable")


class _InitFailure:
    def __call__(self) -> None:
        raise RuntimeError("client bootstrap failed")


class GrobidAdapterTest(unittest.TestCase):
    def test_missing_dependency_is_actionable(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            with self.assertRaises(GrobidDependencyError):
                GrobidAdapter().extract(handle.name)

    def test_adapter_uses_documented_client_shape_when_available(self) -> None:
        client = _ModernFakeClient()
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            result = GrobidAdapter(client_factory=lambda: client).extract(handle.name)

        self.assertEqual(result.title, "Example GROBID Title")
        self.assertEqual(result.authors, ["Ada Lovelace"])
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.doi, "10.1000/example")
        self.assertEqual(result.abstract, "Structured abstract.")
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(client.calls[0]["service"], "processHeaderDocument")
        self.assertIn("output_path", client.calls[0])
        self.assertEqual(client.calls[0]["teiCoordinates"], True)

    def test_adapter_falls_back_to_legacy_client_keywords(self) -> None:
        client = _LegacyFakeClient()
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            result = GrobidAdapter(client_factory=lambda: client).extract(handle.name)

        self.assertEqual(result.title, "Example GROBID Title")
        self.assertEqual(len(client.calls), 3)
        self.assertIn("output_path", client.calls[0])
        self.assertIn("teiCoordinates", client.calls[0])
        self.assertIn("output", client.calls[1])
        self.assertIn("teiCoordinates", client.calls[1])
        self.assertIn("output", client.calls[2])
        self.assertIn("tei_coordinates", client.calls[2])

    def test_runtime_failure_becomes_actionable_dependency_error(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            with self.assertRaisesRegex(GrobidDependencyError, "server unavailable"):
                GrobidAdapter(client_factory=_UnavailableFakeClient).extract(handle.name)

    def test_client_initialization_failure_becomes_actionable_dependency_error(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            with self.assertRaisesRegex(GrobidDependencyError, "client bootstrap failed"):
                GrobidAdapter(client_factory=_InitFailure()).extract(handle.name)

    def test_adapter_uses_configured_grobid_server_when_loading_client(self) -> None:
        captured: dict[str, object] = {}

        class FakeClient:
            def __init__(self, **kwargs: object) -> None:
                captured.update(kwargs)

        grobid_client_module = types.ModuleType("grobid_client")
        grobid_client_impl = types.ModuleType("grobid_client.grobid_client")
        grobid_client_impl.GrobidClient = FakeClient
        grobid_client_module.grobid_client = grobid_client_impl

        with patch.dict(
            sys.modules,
            {
                "grobid_client": grobid_client_module,
                "grobid_client.grobid_client": grobid_client_impl,
            },
        ):
            with patch("synapse.ingest.grobid_adapter.get_settings", return_value=MagicMock(grobid_url="http://grobid:8070")):
                GrobidAdapter()._load_client()

        self.assertEqual(captured["grobid_server"], "http://grobid:8070")

    def test_runtime_hint_is_empty_for_compose_service_url(self) -> None:
        with patch("synapse.ingest.grobid_adapter.os.path.exists", return_value=True):
            self.assertIsNone(GrobidAdapter.runtime_hint("http://grobid:8070"))

    def test_runtime_hint_explains_localhost_inside_container(self) -> None:
        with patch("synapse.ingest.grobid_adapter.os.path.exists", return_value=True):
            hint = GrobidAdapter.runtime_hint("http://localhost:8070")

        self.assertIsNotNone(hint)
        self.assertIn("http://grobid:8070", hint)
        self.assertIn("Compose `grobid` service", hint)

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            GrobidAdapter(client_factory=_ModernFakeClient).extract("missing.pdf")


if __name__ == "__main__":
    unittest.main()
