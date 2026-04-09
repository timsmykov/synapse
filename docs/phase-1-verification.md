# Phase 1 Verification

Date: 2026-04-09

This document records the current Phase 1 verification state for Synapse on the testing VPS.

## Verified Now

- the canonical VPS cycle is working: `git pull` -> `./scripts/deploy_staging.sh` -> `./scripts/run_ingest_smoke.sh` -> `./scripts/check_staging.sh`
- the containerized `synapse ingest --source/--output` contract is green
- the `GROBID optional` policy is green: ingest stays `succeeded` and surfaces GROBID failure as a warning
- the canonical `app`-container canary for `01-ecommerce-meta-analysis.pdf` is green after a clean image rebuild
- canary evaluation confirms `table_extraction_accuracy`, `formula_fidelity`, `provenance_correctness`, and `section_order_correctness`

## Canary Evidence

Canonical canary path:

```bash
cd /srv/synapse/repo
./scripts/run_golden_ingest.sh data/phase1-canary '/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf'
./scripts/evaluate_golden_ingest.sh data/phase1-canary test_corpus/corpus-manifest.json
```

Observed canary result on 2026-04-09:

- emitted output: `/srv/synapse/repo/data/phase1-canary/01-ecommerce-meta-analysis.json`
- evaluation detail: `minimum expected tables=2, actual tables=9; minimum expected table_cells=12, actual table_cells=449`

## Full Batch Evidence On The Current Server Corpus

The currently installed five-document server corpus already has a full emitted output set:

- `/srv/synapse/repo/data/phase1-batch`

Evaluating that output set against the server-side golden manifest is green:

```bash
cd /srv/synapse/repo
/srv/synapse/.venv/bin/python scripts/evaluate_ingest.py \
  data/phase1-batch \
  --manifest /srv/synapse/test_corpus/golden/corpus-manifest.json
```

Observed result on 2026-04-09:

- `passed=true`
- all five selected fixtures passed
- `table_extraction_accuracy`, `formula_fidelity`, `provenance_correctness`, and `section_order_correctness` were green for all five outputs

## Current Blocker

The remaining blocker is now corpus-contract drift, not parser/runtime stability.

There is a mismatch between:

- `/srv/synapse/repo/test_corpus/corpus-manifest.json`
- `/srv/synapse/test_corpus/golden/corpus-manifest.json`

The repo-local manifest describes a newer fixture set with renamed files such as `02-jams-service-review.pdf`.
The server golden corpus still describes the older installed fixture set with files such as `02-service-robot-study.pdf`.

Because of that drift:

- evaluating `data/phase1-batch` against the repo-local manifest fails with a manifest mismatch
- evaluating the same emitted JSON against the matching server manifest passes cleanly

## Phase 1 Status

Phase 1 is partially verified.

Closed:

- canonical testing-box deploy/check/smoke path
- stable ingest CLI contract
- optional GROBID fallback behavior
- green real-PDF canary on the canonical `app` path
- green full-batch evaluation for the corpus currently installed on the server

Still open:

- reconcile the repo-local manifest and the server golden-corpus manifest so the same fixture set is canonical in both places
- rerun the agreed full-batch evaluation after that corpus contract is unified
- only then close the Phase 1 checklist item
