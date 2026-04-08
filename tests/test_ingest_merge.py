from __future__ import annotations

import unittest

from synapse.ingest.merge import merge_document_record
from synapse.ingest.models import (
    DoclingParseResult,
    GrobidMetadataResult,
    ParsedFigure,
    ParsedFormula,
    ParsedSection,
    ParsedTable,
    ParsedTableCell,
)


class IngestMergeTest(unittest.TestCase):
    def test_merge_outputs_document_record(self) -> None:
        structure = DoclingParseResult(
            document_id="paper-1",
            title="Docling Title",
            source_uri="paper-1.pdf",
            sections=[ParsedSection(heading="Intro", text="Section text")],
            tables=[
                ParsedTable(
                    caption="Table 1",
                    rows=1,
                    columns=1,
                    cells=[ParsedTableCell(row=1, column=1, value="A")],
                )
            ],
            formulas=[ParsedFormula(latex="E=mc^2")],
            figures=[ParsedFigure(caption="Figure 1", figure_type="chart")],
        )
        metadata = GrobidMetadataResult(
            source_uri="paper-1.pdf",
            title="Merged Title",
            authors=["Ada Lovelace"],
            year=2024,
            doi="10.1000/example",
            abstract="Structured abstract.",
        )

        record = merge_document_record(structure, metadata)

        self.assertEqual(record.title, "Merged Title")
        self.assertEqual(record.authors, ["Ada Lovelace"])
        self.assertEqual(record.doi, "10.1000/example")
        self.assertEqual(len(record.artifacts), 4)
        self.assertEqual(record.artifacts[0].artifact_type, "section")


if __name__ == "__main__":
    unittest.main()
