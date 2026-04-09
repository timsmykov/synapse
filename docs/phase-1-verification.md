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

Canonical evaluation command:

```bash
cd /srv/synapse/repo
PYTHONPATH=src /srv/synapse/.venv/bin/python \
  scripts/evaluate_ingest.py \
  /srv/synapse/repo/data/phase1-seq-full \
  --manifest /srv/synapse/repo/test_corpus/corpus-manifest.json
```

The evaluation CLI output should always surface:

- `manifest_path`
- `ingest_output`
- `evaluated_document_ids`
- `passed_document_ids` and `failed_document_ids` when coverage is complete
- `missing_document_ids` when coverage is incomplete

Successful full-golden example:

```json
{
  "evaluated_document_ids": [
    "handoyo-2024-meta-analysis",
    "blut-2021-jams",
    "oprea-bra-2025-ebusiness",
    "nguyen-2023-chatbots-frontline",
    "masciari-2024-ai-ethics"
  ],
  "failed_document_ids": [],
  "ingest_output": "/srv/synapse/repo/data/phase1-seq-full",
  "manifest_path": "/srv/synapse/repo/test_corpus/corpus-manifest.json",
  "passed": true,
  "passed_document_ids": [
    "handoyo-2024-meta-analysis",
    "blut-2021-jams",
    "oprea-bra-2025-ebusiness",
    "nguyen-2023-chatbots-frontline",
    "masciari-2024-ai-ethics"
  ],
  "report_count": 5,
  "reports": [
    {
      "document_id": "handoyo-2024-meta-analysis",
      "fixture_file_name": "01-ecommerce-meta-analysis.pdf",
      "passed": true
    }
  ]
}
```

Coverage failure example:

```json
{
  "error": "ingest outputs do not cover the full corpus manifest; missing document_ids: masciari-2024-ai-ethics",
  "evaluated_document_ids": [
    "handoyo-2024-meta-analysis",
    "blut-2021-jams",
    "oprea-bra-2025-ebusiness",
    "nguyen-2023-chatbots-frontline"
  ],
  "ingest_output": "/srv/synapse/repo/data/phase1-seq-full",
  "manifest_path": "/srv/synapse/repo/test_corpus/corpus-manifest.json",
  "missing_document_ids": [
    "masciari-2024-ai-ethics"
  ],
  "passed": false,
  "reports": []
}
```

## Residual Hardening Note

The testing box still shows intermittent `GROBID` DNS resolution failures inside the `app` container during some runs. The full Phase 1 verification pass still succeeds because the baseline parser path is allowed to fall back to Docling-only output.

This remains a separate testing-box hardening issue and does not reopen Phase 1 under the current warning-only fallback policy.

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
