from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

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

    def test_missing_file_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            GrobidAdapter(client_factory=_ModernFakeClient).extract("missing.pdf")


if __name__ == "__main__":
    unittest.main()
