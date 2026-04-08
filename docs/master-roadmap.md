# Synapse Master Roadmap

This is the single source of truth for technical execution.
It consolidates the Notion sources and the repo-level checklist into one operational roadmap.

## Goal

Build Synapse as a CLI-first, self-hosted research context layer for systematic reviews and meta-analyses.
The product must preserve provenance at every extraction step and keep CLI/API entrypoints thin.

## Current Baseline

Already done:

- repository reset from the old landing page codebase
- Python package scaffold, CLI entrypoint, FastAPI app, Docker/Makefile, env template
- canonical `domain` layer for provenance, artifacts, tasks, and request/response contracts
- shared `services` layer between CLI and API
- reserved package boundaries for `ingest`, `storage`, `retrieval`, and `primitives`
- test corpus contract and evaluation contract
- smoke tests for config, CLI, services, and API

## Execution Order

1. Test corpus and evaluation gates
2. Ingestion contract
3. Docling adapter
4. GROBID adapter
5. Merge contract into `DocumentRecord`
6. First JSON ingest output
7. Storage persistence
8. Retrieval/indexing
9. Advanced parsing for figures and formulas
10. Science primitives and orchestration
11. Hardening and release baseline

## Phase Plan

### Phase 0. Foundation

Status: done.

The repo now has the structural baseline required for Day 1 work.

### Phase 1. Ingestion Contract And Parsing Pipeline

Next work:

- define ingest IO contract
- implement Docling adapter
- implement GROBID adapter
- define merge rules into `DocumentRecord`
- emit structured JSON before persistence
- add golden fixtures for tables, formulas, and multi-column layout

Success means:

- `synapse ingest <pdf>` produces structured JSON
- provenance is preserved for sections, tables, cells, formulas, and figures
- contract tests pass on canonical domain shapes

### Phase 2. Storage And Persistence Layer

After ingestion is stable:

- define storage interfaces
- add PostgreSQL migrations/schema
- add MinIO artifact storage
- wire persistence from ingest to storage
- bootstrap local infra health checks

### Phase 3. Retrieval And Indexing Layer

After persistence is stable:

- define retrieval contract
- build repository/query layer
- add LlamaIndex as an indexing facade
- add structured `synapse query` output

### Phase 4. Advanced Parsing

After basic ingest/retrieval contracts are stable:

- add MinerU or PDF-Extract-Kit boundary
- enrich figures and formulas
- add merge rules and quality gates

### Phase 5. Science Primitives

After retrieval is stable:

- implement consistency, table validation, and PICO primitives
- route `analyze` through services
- add async task contract

### Phase 6. Hardening

Final step:

- stabilize CLI contracts
- add SDK if needed
- complete docs/examples
- verify the full `docker compose up -> ingest -> query -> analyze` flow

## What Is Next Now

The next execution slice is:

1. implement `src/synapse/ingest/docling_adapter.py`
2. implement `src/synapse/ingest/grobid_adapter.py`
3. add `src/synapse/ingest/merge.py`
4. wire `synapse ingest` to emit local JSON output
5. run the first golden fixture through the ingest path

Do not move to storage or retrieval until this slice is green.

## Operating Rules For Agents

- Read this file before starting any technical work.
- Read `docs/implementation-checklist.md` before implementation.
- Work top-down: do not skip phases.
- After finishing a scoped task, update the relevant checkbox status in `docs/implementation-checklist.md`.
- If a task changes the execution order, update this file first, then the checklist.
- Keep entrypoints thin; put logic into `domain`, `services`, or the relevant layer package.
- Treat the checklist as the progress ledger and this file as the strategic execution map.

