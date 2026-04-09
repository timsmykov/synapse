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
- CI workflow skeleton for lint, test, compose validation, and image build
- remote testing-box deploy skeleton under `deploy/` and `scripts/`

## Operational Baseline

The repo should target three execution environments:

- local Mac for code editing and external document handling only
- CI for mandatory validation on every push/PR
- a remote single-node testing box for integrated service testing and manual QA

This does not change the product build order. It defines where each class of testing and deployment should happen.

Current remote target assumption:

- one VPS is acceptable for shared testing and early private demos
- current operator-provided host is `ssh root@194.163.181.122`
- treat a 4 vCPU / 8 GB RAM / 100+ GB disk class machine as the minimum practical starter box
- do not colocate heavy local LLM inference on that same node during the MVP phase
- keep ingest concurrency conservative until parser memory profiles are measured on real PDFs

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

Status: verified for the current selected corpus baseline.

Closed in this slice:

- ingest IO contract for single PDF, directory, and glob sources
- Docling adapter normalization into structured parser output
- GROBID metadata adapter with optional dependency fallback
- merge rules into canonical `DocumentRecord`
- structured JSON output from `synapse ingest`
- contract coverage for ingest IO and merge behavior

Closed with the current server verification pass:

- canonical VPS full golden sweep on the selected five-document corpus
- strict full-corpus evaluation against the repo-local manifest
- green Day 1 metric pass for all five emitted outputs

Operational follow-up, but not a Phase 1 blocker:

- harden `GROBID` service discovery inside the testing-box `app` container

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
- prepare the remote testing compose profile once Postgres, Redis, and MinIO contracts are stable

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
- wire CI gates for lint, unit, contract, and compose smoke tests
- formalize the single-node testing deploy path with isolated compose project and high-port loopback bindings
- separate staging and production once traffic or ingest concurrency justifies another node

## What Is Next Now

The next execution slice is:

1. begin Phase 2 storage interfaces and persistence path
2. keep the current verified five-document corpus as the active acceptance baseline until a larger corpus wave is added intentionally
3. close the separate testing-box hardening issue around intermittent `GROBID` DNS resolution

Do not move to retrieval until Phase 2 storage work is green.

## Testing And Deploy Policy

Use this operating model during the MVP:

1. Edit code locally if convenient, but do not rely on Mac-local installs or runtime.
2. Run repeatable validation in CI before deploy.
3. Run installs, integrated parser/storage tests, and manual QA on the remote testing box.
4. Treat production as a later isolation step, not as a prerequisite for Phase 1-3 delivery.

## Operating Rules For Agents

- Read this file before starting any technical work.
- Read `docs/implementation-checklist.md` before implementation.
- Work top-down: do not skip phases.
- After finishing a scoped task, update the relevant checkbox status in `docs/implementation-checklist.md`.
- If a task changes the execution order, update this file first, then the checklist.
- Keep entrypoints thin; put logic into `domain`, `services`, or the relevant layer package.
- Treat the checklist as the progress ledger and this file as the strategic execution map.
