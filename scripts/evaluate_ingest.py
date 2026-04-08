#!/usr/bin/env python3
"""Evaluate ingest JSON outputs against the golden corpus manifest."""

from __future__ import annotations

import argparse
import json

from synapse.evaluation import evaluate_ingest_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ingest_output",
        help="Path to one ingest JSON file or a directory of JSON files",
    )
    parser.add_argument(
        "--manifest",
        default="test_corpus/corpus-manifest.template.json",
        help="Path to the corpus manifest JSON file",
    )
    args = parser.parse_args()

    reports = evaluate_ingest_outputs(args.manifest, args.ingest_output)
    payload = {
        "reports": [report.model_dump(mode="json") for report in reports],
        "passed": all(report.passed for report in reports),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
