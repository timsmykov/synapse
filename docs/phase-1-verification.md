# Phase 1 Verification

Date: 2026-04-09

This document records the explicit verification pass for Phase 1 of Synapse: ingest contracts, parser fallback behavior, provenance truthfulness, and the current VPS-backed golden-PDF verification path.

## Scope

- verify the canonical testing-box cycle on the VPS
- verify the `synapse ingest --source/--output` CLI contract on the containerized path
- verify the `GROBID optional` fallback policy on a real PDF pass
- verify provenance truthfulness after the confidence/parser fixes
- run evaluation on emitted real-PDF JSON from the VPS container path
- distinguish the old isolated-container result from the current canonical `app`-container path
- distinguish debugging canaries from the full-corpus acceptance gate

## Canonical VPS Cycle

Verified working on the testing box at `194.163.181.122`:

1. `git pull`
2. `./scripts/deploy_staging.sh`
3. `./scripts/check_staging.sh`
4. `./scripts/run_ingest_smoke.sh`

The deploy/check/smoke scripts still reflect the intended canonical flow for the Phase 1 baseline.

## Evidence

Two different real-PDF paths were exercised on 2026-04-09:

- an older isolated container path that was useful for debugging parser/runtime behavior
- the canonical `app`-container path introduced later via `scripts/run_golden_ingest.sh`

Only the canonical `app`-container path should be treated as the current verification baseline.
Only a full emitted output set that covers every selected manifest fixture counts as Phase 1 acceptance evidence.

### Earlier Isolated Container Pass

Real golden-PDF ingest was run on the VPS with an isolated container and OCR disabled:

```bash
docker run --rm --name synapse-phase1-final \
  -e HF_HOME=/cache/hf \
  -e SYNAPSE_PARSER_OCR_ENABLED=0 \
  -e SYNAPSE_GROBID_URL=http://localhost:8070 \
  -v /srv/synapse/model-cache/hf:/cache/hf \
  -v /srv/synapse/model-cache/rapidocr:/usr/local/lib/python3.12/site-packages/rapidocr/models \
  -v /srv/synapse/repo:/workspace \
  -v /srv/synapse/test_corpus:/workspace/test_corpus \
  synapse-testing:latest \
  synapse ingest \
    --source /workspace/test_corpus/golden/01-ecommerce-meta-analysis.pdf \
    --output /workspace/data/phase1-final
```

Observed result on 2026-04-09:

- container exit code: `0`
- emitted output: `/srv/synapse/repo/data/phase1-final/01-ecommerce-meta-analysis.json`
- ingest receipt: `status=succeeded`
- ingest receipt parser: `docling`
- ingest receipt artifact count: `427`
- receipt warning captured the expected `GROBID optional` fallback because `http://localhost:8070` was not reachable from the isolated container

Evaluation was then run against the emitted JSON:

```bash
cd /srv/synapse/repo
/srv/synapse/.venv/bin/python scripts/evaluate_ingest.py \
  /srv/synapse/repo/data/phase1-final \
  --manifest /srv/synapse/repo/test_corpus/corpus-manifest.json
```

Observed evaluation result on 2026-04-09:

- `provenance_correctness`: passed
- `section_order_correctness`: passed
- `formula_fidelity`: passed
- `table_extraction_accuracy`: passed
- success detail: `minimum expected tables=2, actual tables=9; minimum expected table_cells=12, actual table_cells=449`

This pass was valuable as a debugging milestone, but it is not the current canonical verification path because it used an isolated container with `SYNAPSE_GROBID_URL=http://localhost:8070`.

### Current Canonical `app`-Container Pass

The current scaffold path runs real PDFs through the already running `app` service:

```bash
./scripts/run_golden_ingest.sh data/phase1-canary '/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf'
./scripts/evaluate_golden_ingest.sh data/phase1-canary test_corpus/corpus-manifest.json
```

Observed ingest result on 2026-04-09 after a clean `app` image rebuild from the current server checkout:

- emitted output: `/srv/synapse/repo/data/phase1-canary/01-ecommerce-meta-analysis.json`
- ingest receipt: `status=succeeded`
- receipt warning still captures the expected `GROBID optional` fallback
- canary evaluation from the server repo checkout is a debugging milestone only, not a closing Phase 1 gate
- after the strict full-corpus gate was introduced, evaluating `data/phase1-canary` alone is expected to fail because the output directory does not cover the full manifest fixture set
- the canary still confirms the table-extraction detail on this fixture: `minimum expected tables=2, actual tables=9; minimum expected table_cells=12, actual table_cells=449`

## Verified Phase 1 Baseline

The following Phase 1 claims were confirmed in this pass:

- the canonical VPS deploy/check/smoke cycle is still working
- the containerized `synapse ingest --source/--output` contract is green
- a real golden PDF now ingests successfully on the VPS container path with OCR disabled
- when GROBID is unavailable, ingest stays succeeded and surfaces the failure as a warning
- top-level document provenance is now truthful: the emitted parser is `docling` when the run is Docling-only
- provenance correctness passes under the updated contract where `bbox` and `confidence` are only required when the parser actually provides them
- the canonical `app`-container real-PDF path emits JSON successfully for `01-ecommerce-meta-analysis.pdf`
- the canonical evaluation path is now unambiguous: server repo checkout plus `scripts/evaluate_golden_ingest.sh` or `scripts/evaluate_ingest.py`
- partial emitted output is now a hard evaluation failure under the strict full-corpus gate

## Confirmed Details

### CLI Contract

The containerized path succeeds with the current CLI contract:

```bash
synapse ingest --source <pdf-or-dir-or-glob> --output <json-file-or-dir>
```

The smoke receipt confirms:

- `status=succeeded`
- `source_uri` and `output_uri` are echoed back in the structured payload
- JSON is written to the requested output path
- `resolved_sources`, `written_files`, and `warnings` are included in the receipt result

### GROBID Optional Policy

The smoke run confirmed the current fallback policy is correct:

- when `GROBID` is unavailable, ingest does not fail
- the receipt stays `succeeded`
- the failure is surfaced as a warning in `receipt.result.warnings`

This is the intended Day 1 behavior for the shared testing box.

## Real PDF Pass

Golden corpus sync was refreshed to the current stable names under `/srv/synapse/test_corpus/golden`, and the first real-PDF pass completed for:

- `01-ecommerce-meta-analysis.pdf`

The runtime blocker from earlier in the day is resolved:

- Docling conversion now completes with OCR disabled on the testing box
- the isolated real-PDF ingest container exits `0`
- the canonical `app` service also emits real-PDF JSON on the VPS
- the current blocker is no longer mount visibility, evaluation execution, or the first table canary on the canonical `app` path
- the remaining blocker is the full selected golden sweep, not the first representative real-PDF pass

## Findings Fixed During Verification

The verification found and fixed the main Phase 1 truthfulness/runtime drifts:

- document-level provenance no longer stamps `docling+grobid` when the run falls back to Docling-only
- `confidence` is now treated as parser-provided optional metadata instead of defaulting to a fake `1.0`
- the evaluation contract now checks `confidence` only when it is actually present
- the Docling adapter now wires the OCR setting through the PDF pipeline options, matching the MVP `OCR disabled` policy
- the Docling adapter now reads modern Docling table exports from `data.table_cells` instead of only the older top-level `cells` shape
- timing and fallback logs were added around the Docling and GROBID workflow path so future real-PDF debugging is evidence-driven

## Residual Risk

Phase 1 is closer to closure, but not fully verified yet.

Open work remains:

- run the full golden-fixture sweep on the VPS container path, not just the first representative PDF
- evaluate only a directory that covers the full selected manifest fixture set; partial output now fails by design
- decide whether the canonical containerized verification path should keep using Docling-only fallback or should be wired to a reachable GROBID endpoint for hybrid runs

## Phase 1 Status

Phase 1 remains partially verified, not fully verified.

Closed in this verification pass:

- canonical testing-box cycle confirmed
- stable `synapse ingest --source/--output` smoke contract confirmed
- `GROBID optional` warning-only policy confirmed
- golden corpus sync refreshed on the VPS
- first real-PDF VPS ingest now completes and emits JSON
- provenance truthfulness is verified on the real pass
- the canonical real-PDF ingest path is fixed at the scaffold level
- the canonical evaluation path is fixed at the scaffold level
- the first canonical `app`-container canary is green again after the clean rebuild delivered the current Docling adapter

Still open before Phase 1 can be closed:

- run the full golden fixture set through the canonical VPS container path
- rerun `scripts/evaluate_ingest.py` or `scripts/evaluate_golden_ingest.sh` on that full output set
- only then mark the Phase 1 checklist item closed
