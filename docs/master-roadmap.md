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
- use `MiniMax` as the primary LLM path and `OpenRouter` for embeddings and other auxiliary model calls
- keep OCR disabled in the default ingest baseline unless scanned-PDF evidence forces it on
- defer `ColPali` until the retrieval phase instead of front-loading it into MVP ingest

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

## Phase model vs workstreams

Do not replace the phase model with component-only planning.

The current phases are still correct because they encode dependency order:

- Phase 1 must stabilize ingest contracts before persistence
- Phase 2 must stabilize storage before retrieval
- retrieval must stabilize before science primitives

What should change is execution inside each phase:

- one `scaffold` lane owns repo/runtime integration
- multiple `component` lanes own isolated modules within the current phase
- integration happens through the scaffold lane, not by letting all agents touch the same seams

This means the project is still phased, but implemented through component workstreams.

## Phase Plan

### Phase 0. Foundation

Status: done.

The repo now has the structural baseline required for Day 1 work.

### Phase 1. Ingestion Contract And Parsing Pipeline

Status: in progress.

Recommended Phase 1 workstream split:

- `scaffold`: testing-box cycle, CLI/service wiring, deploy path, verification docs, roadmap/checklist
- `docling`: parser runtime options, section/table extraction, parser-specific tests
- `grobid`: client bootstrap, container networking assumptions, metadata/citation extraction
- `merge/eval`: canonical `DocumentRecord`, artifact merge rules, corpus thresholds, golden evaluation analysis

Closed in this slice:

- ingest IO contract for single PDF, directory, and glob sources
- Docling adapter normalization into structured parser output
- GROBID metadata adapter with optional dependency fallback
- merge rules into canonical `DocumentRecord`
- structured JSON output from `synapse ingest`
- contract coverage for ingest IO and merge behavior

Remaining:

- reconcile the repo-local fixture manifest and the server golden-corpus manifest into one canonical selected set
- rerun the full-batch evaluation on that unified corpus contract

Current blocker on the testing box:

- the current server corpus is green, but repo and server now disagree about which fixture set is canonical

Current blocking gaps from the 2026-04-09 testing-box pass:

- the canonical `app`-container canary is green again with `actual tables=9` and `actual table_cells=449`
- the full currently installed server corpus is green when evaluated against `/srv/synapse/test_corpus/golden/corpus-manifest.json`
- the repo-local `test_corpus/corpus-manifest.json` describes a different renamed fixture set, so the same emitted JSON fails against the repo manifest
- the remaining blocker is corpus-contract reconciliation, not parser/runtime stabilization on the current server corpus

Success means:

- `synapse ingest <pdf>` produces structured JSON
- provenance is preserved for sections, tables, cells, formulas, and figures, with `bbox` and `confidence` carried through when the parser actually provides them
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

1. reconcile `test_corpus/corpus-manifest.json` with `/srv/synapse/test_corpus/golden/corpus-manifest.json`
2. keep exactly one canonical selected fixture set across repo and server
3. rerun the agreed full-batch evaluation on that unified contract
4. begin Phase 2 storage interfaces only after that unified golden gate is green

Do not move to storage or retrieval until this slice is green.

## Testing And Deploy Policy

Use this operating model during the MVP:

1. Edit code locally if convenient, but do not rely on Mac-local installs or runtime.
2. Run repeatable validation in CI before deploy.
3. Run installs, integrated parser/storage tests, and manual QA on the remote testing box.
4. Treat production as a later isolation step, not as a prerequisite for Phase 1-3 delivery.

Hard policy:

- the Mac is not an approved Synapse runtime target
- do not maintain local project environments or local compose verification on the Mac
- when local runtime artifacts appear, delete them and continue from the server

## Operating Rules For Agents

- Read this file before starting any technical work.
- Read `docs/implementation-checklist.md` before implementation.
- Work top-down: do not skip phases.
- After finishing a scoped task, update the relevant checkbox status in `docs/implementation-checklist.md`.
- If a task changes the execution order, update this file first, then the checklist.
- Keep entrypoints thin; put logic into `domain`, `services`, or the relevant layer package.
- Treat the checklist as the progress ledger and this file as the strategic execution map.
- Prefer component ownership over free-form parallelism.
- Keep `scaffold` ownership singular; do not let multiple agents edit the same integration seam in parallel.
