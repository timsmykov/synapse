# Phase 1 Verification

Date: 2026-04-09

This document records the current Phase 1 verification state for Synapse on the testing VPS.

## Canonical Server Flow

Verified on `ssh root@194.163.181.122`:

1. `./scripts/deploy_staging.sh`
2. `./scripts/check_staging.sh`
3. `./scripts/run_ingest_smoke.sh`
4. `./scripts/run_golden_ingest.sh data/phase1-seq-full`
5. `./scripts/evaluate_golden_ingest.sh data/phase1-seq-full test_corpus/corpus-manifest.json`

The canonical server-side golden ingest helper now expands the fixture set on the host and runs one PDF at a time through the running `app` container. This avoids the earlier opaque full-batch path and keeps the emitted output set inspectable while the run is in flight.

## Verified Now

- the canonical VPS cycle is working: deploy, check, smoke, full golden ingest, strict evaluation
- the containerized `synapse ingest --source/--output` contract is green
- the strict full-corpus evaluation gate is green on the selected five-document golden set
- provenance correctness, section ordering, table extraction, and formula fidelity all pass on the full emitted output set
- the selected Phase 1 fixture set is now verified end-to-end on the VPS against the repo-local manifest

## Full Golden Sweep Evidence

Canonical full run on 2026-04-09:

```bash
cd /srv/synapse/repo
./scripts/run_golden_ingest.sh data/phase1-seq-full
```

Observed emitted output set:

- `/srv/synapse/repo/data/phase1-seq-full/01-ecommerce-meta-analysis.json`
- `/srv/synapse/repo/data/phase1-seq-full/02-service-robot-study.json`
- `/srv/synapse/repo/data/phase1-seq-full/03-anthropomorphism-meta-analysis.json`
- `/srv/synapse/repo/data/phase1-seq-full/04-ai-systematic-review.json`
- `/srv/synapse/repo/data/phase1-seq-full/05-ai-ethics-review.json`

Observed ingest receipts:

- `01-ecommerce-meta-analysis.pdf`: `artifact_count=427`, parser=`docling`, warnings=`[]`
- `02-service-robot-study.pdf`: `artifact_count=508`, parser=`docling`, warning-only GROBID fallback
- `03-anthropomorphism-meta-analysis.pdf`: `artifact_count=445`, parser=`docling`, warning-only GROBID fallback
- `04-ai-systematic-review.pdf`: `artifact_count=464`, parser=`docling`, warning-only GROBID fallback
- `05-ai-ethics-review.pdf`: `artifact_count=608`, parser=`docling`, warning-only GROBID fallback

## Strict Evaluation Evidence

Strict evaluation was run from the branch checkout against the full emitted output set:

```bash
cd /srv/synapse/worktrees/phase1-gate-hardening
/srv/synapse/.venv/bin/python scripts/evaluate_ingest.py \
  /srv/synapse/repo/data/phase1-seq-full \
  --manifest test_corpus/corpus-manifest.json
```

Observed result on 2026-04-09:

- `passed=true`
- all five selected fixtures matched the manifest and passed all Day 1 metrics

Per-fixture highlights:

- `01-ecommerce-meta-analysis.pdf`: `tables=9`, `table_cells=449`
- `02-service-robot-study.pdf`: `tables=7`, `table_cells=568`
- `03-anthropomorphism-meta-analysis.pdf`: `tables=9`, `table_cells=1034`
- `04-ai-systematic-review.pdf`: `tables=4`, `table_cells=284`
- `05-ai-ethics-review.pdf`: `tables=14`, `table_cells=524`

All five passed:

- `table_extraction_accuracy`
- `formula_fidelity`
- `provenance_correctness`
- `section_order_correctness`

## Operational Note

The current testing-box baseline still shows intermittent `GROBID` hostname resolution failures from inside the `app` container:

- `http://grobid:8070` occasionally resolves to a `NameResolutionError`
- the current ingest contract treats this as a warning-only fallback
- the full Phase 1 verification pass still succeeds because the baseline parser path is allowed to fall back to Docling-only output

This is still an operational issue worth hardening, but it is not a blocker for Phase 1 closeout under the current fallback policy.

## Phase 1 Status

Phase 1 is verified for the current selected corpus baseline.

Closed:

- canonical testing-box deploy/check/smoke path
- stable ingest CLI contract
- strict full-corpus evaluation gate
- canonical VPS full golden sweep on the selected five-document corpus
- full green Day 1 metric pass on the emitted output set

Open after Phase 1 closeout:

- harden `GROBID` service discovery inside the testing-box `app` container
- decide whether future verification should require hybrid Docling+GROBID output or keep the current Docling-first fallback baseline
