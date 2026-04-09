"""GROBID adapter boundary for Synapse Phase 1 ingestion."""

from __future__ import annotations

import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from synapse.config import get_settings

from .models import GrobidMetadataResult


class GrobidDependencyError(RuntimeError):
    """Raised when GROBID integration is requested without its Python client installed."""


class GrobidAdapter:
    """Extract title/citation metadata via grobid-client-python."""

    def __init__(self, client_factory: Callable[[], Any] | None = None) -> None:
        self._client_factory = client_factory

    def extract(self, source_uri: str) -> GrobidMetadataResult:
        source_path = Path(source_uri)
        if not source_path.exists():
            raise FileNotFoundError(source_uri)

        try:
            client = self._client_factory() if self._client_factory else self._load_client()
            tei_xml = self._run_grobid(client, source_path)
        except GrobidDependencyError:
            raise
        except Exception as exc:
            raise GrobidDependencyError(f"GROBID extraction is unavailable: {exc}") from exc
        return self._parse_tei(tei_xml, str(source_path))

    @classmethod
    def runtime_hint(cls, grobid_url: str) -> str | None:
        parsed = urlparse(grobid_url)
        if parsed.hostname not in {"localhost", "127.0.0.1"}:
            return None
        if not cls._is_container_runtime():
            return None
        return (
            " SYNAPSE_GROBID_URL points at localhost from inside a container, which "
            "resolves to the container itself, not the Compose `grobid` service. "
            "Use the canonical app container path or set SYNAPSE_GROBID_URL to "
            "`http://grobid:8070` on the Compose network."
        )

    def _load_client(self) -> Any:
        try:
            from grobid_client.grobid_client import GrobidClient
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency optional.
            raise GrobidDependencyError(
                "grobid-client-python is not installed. Install Synapse with the `research` "
                "extras or provide a client_factory for tests."
            ) from exc
        return GrobidClient(grobid_server=get_settings().grobid_url)

    @staticmethod
    def _is_container_runtime() -> bool:
        return os.path.exists("/.dockerenv")

    @staticmethod
    def _run_grobid(client: Any, source_path: Path) -> str:
        with (
            tempfile.TemporaryDirectory() as input_dir,
            tempfile.TemporaryDirectory() as output_dir,
        ):
            staged_source = Path(input_dir) / source_path.name
            shutil.copy2(source_path, staged_source)

            attempts = (
                {
                    "service": "processHeaderDocument",
                    "input_path": input_dir,
                    "output_path": output_dir,
                    "n": 1,
                    "consolidate_header": True,
                    "teiCoordinates": True,
                    "force": True,
                },
                {
                    "service": "processHeaderDocument",
                    "input_path": input_dir,
                    "output": output_dir,
                    "n": 1,
                    "consolidate_header": True,
                    "teiCoordinates": True,
                    "force": True,
                },
                {
                    "service": "processHeaderDocument",
                    "input_path": input_dir,
                    "output": output_dir,
                    "n": 1,
                    "consolidate_header": True,
                    "tei_coordinates": True,
                    "force": True,
                },
            )

            last_error: TypeError | None = None
            for kwargs in attempts:
                try:
                    client.process(**kwargs)
                    break
                except TypeError as exc:
                    last_error = exc
            else:
                raise RuntimeError(
                    "GROBID client.process() signature did not match supported "
                    "grobid-client-python variants."
                ) from last_error

            tei_files = sorted(Path(output_dir).glob("*.tei.xml"))
            if not tei_files:
                raise RuntimeError("GROBID did not produce a TEI output file")
            return tei_files[0].read_text(encoding="utf-8")

    @staticmethod
    def _parse_tei(tei_xml: str, source_uri: str) -> GrobidMetadataResult:
        ns = {"tei": "http://www.tei-c.org/ns/1.0"}
        try:
            root = ET.fromstring(tei_xml)
        except ET.ParseError as exc:
            raise RuntimeError("GROBID returned malformed TEI XML") from exc

        def first_text(path: str) -> str | None:
            node = root.find(path, ns)
            if node is None:
                return None
            text = "".join(node.itertext()).strip()
            return text or None

        authors: list[str] = []
        seen_authors: set[str] = set()
        for author in root.findall(".//tei:author", ns):
            name = " ".join(part.strip() for part in author.itertext() if part.strip())
            if name:
                normalized_name = " ".join(name.split())
                if normalized_name in seen_authors:
                    continue
                seen_authors.add(normalized_name)
                authors.append(normalized_name)

        year = None
        date_node = root.find(".//tei:publicationStmt//tei:date", ns)
        if date_node is not None:
            raw_year = (date_node.get("when") or "".join(date_node.itertext())).strip()
            digits = "".join(ch for ch in raw_year if ch.isdigit())
            if len(digits) >= 4:
                year = int(digits[:4])

        doi = None
        for identifier in root.findall(".//tei:idno", ns):
            identifier_type = (identifier.get("type") or "").lower()
            text = "".join(identifier.itertext()).strip()
            if identifier_type == "doi" and text:
                doi = text
                break

        return GrobidMetadataResult(
            source_uri=source_uri,
            title=first_text(".//tei:titleStmt/tei:title"),
            authors=authors,
            year=year,
            doi=doi,
            abstract=first_text(".//tei:profileDesc/tei:abstract"),
            raw_tei=tei_xml,
        )
