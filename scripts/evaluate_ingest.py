#!/usr/bin/env python3
"""Evaluate ingest JSON outputs against the golden corpus manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    from synapse.evaluation import IngestCoverageError, evaluate_ingest_outputs

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ingest_output",
        help="Path to one ingest JSON file or a directory of JSON files",
    )
    parser.add_argument(
        "--manifest",
        default="test_corpus/corpus-manifest.json",
        help="Path to the corpus manifest JSON file",
    )
    args = parser.parse_args()

    try:
        reports = evaluate_ingest_outputs(args.manifest, args.ingest_output)
    except (IngestCoverageError, KeyError) as exc:
        payload = {
            "reports": [],
            "passed": False,
            "error": str(exc),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    payload = {
        "reports": [report.model_dump(mode="json") for report in reports],
        "passed": all(report.passed for report in reports),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
