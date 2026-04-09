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

The current scaffold launcher for a full five-document pass is now the updated sequential helper:

```bash
cd /srv/synapse/worktrees/phase1-gate-hardening
./scripts/run_golden_ingest.sh data/phase1-golden-full
```

This path now starts correctly and writes per-file logs such as:

- `/srv/synapse/worktrees/phase1-gate-hardening/data/phase1-golden-full/run-01.log`

However, the first document in the batch still does not complete on the current VPS.

## Current Blocker

The remaining blocker is now VPS memory pressure during the full-batch path.

Observed failure on 2026-04-09:

- the sequential full-batch launcher starts normally on the updated PR worktree
- `run-01.log` is created for `01-ecommerce-meta-analysis.pdf`
- the `synapse ingest` process inside `app` is OOM-killed before the first JSON is emitted

Evidence from `dmesg` on the VPS:

- `Out of memory: Killed process 541264 (synapse) ... anon-rss:1489124kB`

This means the current blocker is no longer canary correctness or stale launcher logic.
It is the memory envelope of the shared testing box when the full-batch path runs inside the long-lived `app` container.

## Phase 1 Status

Phase 1 is partially verified.

Closed:

- canonical testing-box deploy/check/smoke path
- stable ingest CLI contract
- optional GROBID fallback behavior
- green real-PDF canary on the canonical `app` path
- working sequential full-batch launcher in the updated PR worktree

Still open:

- complete the full-batch pass without OOM-killing the `synapse ingest` process on the VPS
- rerun full-batch evaluation after the memory/runtime blocker is removed
- only then close the Phase 1 checklist item
