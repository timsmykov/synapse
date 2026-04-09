from __future__ import annotations

import argparse
import faulthandler
import logging
import sys
from pathlib import Path
from time import perf_counter

from synapse.ingest.docling_adapter import DoclingAdapter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a focused DoclingAdapter.convert() debug pass on one PDF."
    )
    parser.add_argument("source", help="Path to the PDF source")
    parser.add_argument(
        "--output",
        help="Optional path to write the normalized Docling parse result as JSON",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Emit faulthandler stack dumps if conversion exceeds this duration",
    )
    parser.add_argument(
        "--ocr-enabled",
        action="store_true",
        help="Explicitly enable OCR for this debug run",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    source_path = Path(args.source).expanduser()
    output_path = Path(args.output).expanduser() if args.output else None
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    faulthandler.enable()
    faulthandler.dump_traceback_later(args.timeout_seconds, repeat=True)

    started = perf_counter()
    logging.info(
        "Starting DoclingAdapter.convert for %s with OCR %s",
        source_path,
        "enabled" if args.ocr_enabled else "disabled",
    )
    result = DoclingAdapter(ocr_enabled=args.ocr_enabled).convert(source_path)
    elapsed = perf_counter() - started
    faulthandler.cancel_dump_traceback_later()

    logging.info(
        "DoclingAdapter.convert finished in %.2fs: sections=%s tables=%s formulas=%s figures=%s",
        elapsed,
        len(result.sections),
        len(result.tables),
        len(result.formulas),
        len(result.figures),
    )

    if output_path is not None:
        output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        logging.info("Wrote normalized Docling result to %s", output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
