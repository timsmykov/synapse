# Phase 1 Verification

Date: 2026-04-09

This document records the current Phase 1 verification state for Synapse on the testing VPS.

## Verified Now

- the canonical VPS cycle is working: `git pull` -> `./scripts/deploy_staging.sh` -> `./scripts/run_ingest_smoke.sh` -> `./scripts/check_staging.sh`
- the containerized `synapse ingest --source/--output` contract is green
- the `GROBID optional` policy is green: ingest stays `succeeded` and surfaces GROBID failure as a warning
- the canonical `app`-container canary for `01-ecommerce-meta-analysis.pdf` is green after a clean image rebuild
- canary evaluation confirms `table_extraction_accuracy`, `formula_fidelity`, `provenance_correctness`, and `section_order_correctness`
- the full selected server corpus now passes through the isolated per-document launcher without OOM

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

The stable full-batch path on the current VPS is now the isolated per-document launcher:

```bash
cd /srv/synapse/repo
./scripts/run_golden_ingest_isolated.sh data/phase1-isolated-full
```

Observed result on 2026-04-09:

- `exit=0`
- all five selected fixtures emitted JSON under `/srv/synapse/repo/data/phase1-isolated-full`
- per-file logs were written as `run-01.log` through `run-05.log`
- all five isolated runs completed with `warnings=[]`

Canonical evaluation command on the VPS:

```bash
cd /srv/synapse/repo
/srv/synapse/.venv/bin/python scripts/evaluate_ingest.py \
  data/phase1-isolated-full \
  --manifest /srv/synapse/test_corpus/golden/corpus-manifest.json
```

Observed evaluation result on 2026-04-09:

- `passed=true`
- all five selected fixtures passed
- `table_extraction_accuracy`, `formula_fidelity`, `provenance_correctness`, and `section_order_correctness` were green for all five outputs

## Current Blocker

The remaining blocker is now corpus-contract drift, not parser/runtime stability on the server corpus.

There is a mismatch between:

- `/srv/synapse/repo/test_corpus/corpus-manifest.json`
- `/srv/synapse/test_corpus/golden/corpus-manifest.json`

The repo-local manifest describes a newer renamed fixture set.
The server golden corpus still describes the currently installed fixture set with files such as `02-service-robot-study.pdf`.

Because of that drift:

- evaluating the green server output sets against the repo-local manifest still fails with a manifest mismatch
- evaluating the same emitted JSON against the matching server golden manifest passes cleanly

## Phase 1 Status

Phase 1 is partially verified.

Closed:

- canonical testing-box deploy/check/smoke path
- stable ingest CLI contract
- optional GROBID fallback behavior
- green real-PDF canary on the canonical `app` path
- green full-batch isolated-per-document sweep for the current server corpus

Still open:

- reconcile the repo-local manifest and the server golden-corpus manifest so the same fixture set is canonical in both places
- rerun the agreed full-batch evaluation after that corpus contract is unified
- only then close the Phase 1 checklist item
