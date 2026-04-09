# Synapse Architecture

## Product
Synapse is a CLI-first research context layer for systematic reviews and meta-analysis.
It is not a general chat app and not a browser extension.
The core value is traceable extraction from scientific PDFs into verifiable structured data.

## MVP stack
- Language: Python 3.12
- CLI: Typer
- API: FastAPI
- Orchestration: LangGraph and Celery
- Parsing: Docling and GROBID first; OCR disabled by default in the MVP path; MinerU or PDF-Extract-Kit later where they materially improve figure and formula extraction
- Storage: PostgreSQL 16+ with JSONB and pgvector, MinIO, Redis
- Retrieval: LlamaIndex with hybrid vector + keyword + metadata search
- Deployment: Docker Compose first, Kubernetes later
- Validation: CI gates plus server-side smoke and integration checks

## Environments
- Local Mac is for source editing, review, and document preparation only.
- CI is the mandatory validation gate for lint, unit, contract, and compose smoke checks before deploy.
- Remote testing runs on a single self-hosted VPS with Docker Compose, Postgres, Redis, MinIO, GROBID, reverse proxy, and the Synapse app service.
- Current testing host assumption: `ssh root@194.163.181.122` for bootstrap, runtime, and manual test operation.
- Production should move to a separate node once usage or parsing concurrency grows beyond private MVP traffic.
- A single VPS is acceptable for shared testing and low-traffic private demos only as a temporary step, and only without colocating heavy local LLM inference on the same machine.

## Runtime policy
- Use the remote VPS as the default execution environment for installs, tests, runtime, and manual QA.
- Keep the Mac out of the runtime path; use it for editing code and handling external source documents.
- Do not maintain a project-local Python environment, local Docker stack, or local deploy/test baseline on the Mac for Synapse.
- If a local runtime artifact appears on the Mac, remove it and continue using the server as the only execution environment.
- Treat GROBID and document parsing as memory-sensitive workloads; keep ingest concurrency low on the first VPS tier.
- Do not expose Postgres, Redis, or MinIO directly to the public internet.
- Put the externally reachable API behind a reverse proxy such as Caddy or Nginx when that becomes necessary.
- Keep the Synapse stack isolated under its own Docker Compose project name so it does not interfere with unrelated server workloads.
- Use API-backed model providers on the VPS; do not install local LLM runtimes there.
- Use `MiniMax` as the primary agent/base LLM provider.
- Use `OpenRouter` for embeddings and other non-primary model routing.
- Keep OCR disabled on the default ingest path until the born-digital PDF baseline is stable.
- Keep `ColPali` out of the MVP critical path until the retrieval layer is ready for a visual retrieval experiment.

## Code boundaries
- `src/synapse/domain/` owns canonical artifacts, provenance, and request/response models.
- `src/synapse/services/` owns use cases shared by CLI and API.
- `src/synapse/ingest/` owns parser adapters and normalization.
- `src/synapse/storage/` owns Postgres, MinIO, and queue persistence.
- `src/synapse/retrieval/` owns indexes and query assembly.
- `src/synapse/primitives/` owns review-specific analysis primitives.

## Execution model

The roadmap phases stay as-is.
They define dependency order correctly.

What changes is the execution model inside a phase:

- keep one `scaffold` workstream for repo/runtime integration
- split feature work into component workstreams with disjoint ownership
- do not let multiple agents edit the same integration seams in parallel

### Scaffold workstream

This is the project carcass.
It should have one owner at a time.

- `src/synapse/config.py`
- `src/synapse/cli.py`
- `src/synapse/server.py`
- `src/synapse/domain/`
- `src/synapse/services/`
- `deploy/`
- `scripts/deploy_staging.sh`
- `scripts/check_staging.sh`
- `scripts/run_ingest_smoke.sh`
- CI, environment contracts, roadmap/checklist updates

The scaffold owner is responsible for:

- canonical CLI and service contracts
- deploy/runtime wiring
- testing-box workflow
- phase status, sequencing, and verification artifacts
- integrating component outputs into the canonical app path

### Component workstreams

Components should be developed in parallel, but with file-level ownership:

- `Docling component`: `src/synapse/ingest/docling_adapter.py` and its tests
- `GROBID component`: `src/synapse/ingest/grobid_adapter.py` and its tests
- `Merge/normalize component`: `src/synapse/ingest/merge.py`, `src/synapse/ingest/models.py`, merge/domain contract tests
- `Evaluation/golden component`: ingest evaluation logic, corpus manifest, verification analysis, thresholds
- later phases: `storage/`, `retrieval/`, `primitives/` each become their own components

### Coordination rule

Component owners should not edit scaffold files unless the scaffold owner explicitly hands them that write scope.

In particular, component agents should avoid parallel edits to:

- `src/synapse/services/workflows.py`
- `src/synapse/cli.py`
- `src/synapse/config.py`
- roadmap/checklist/deploy docs

This keeps the integration seam stable while component work advances in parallel.

## Core flow
1. `synapse ingest` accepts PDFs and writes raw artifacts to object storage.
2. Parsing normalizes document structure, tables, formulas, figures, metadata, and provenance.
3. Data is stored in Postgres with traceability fields for page, bbox, confidence, and source doc.
4. Retrieval exposes document, section, table cell, formula, and figure level search.
5. Analysis commands run review-oriented primitives such as consistency checks and PICO extraction.

## Design rules
- Keep every extracted fact traceable back to a source page and bounding box when possible.
- Prefer open-source components with permissive licenses.
- Avoid bespoke parsing code unless an integration gap forces it.
- Keep the CLI stable; other interfaces are secondary.
- Keep the first release self-hosted by default.

## Non-goals for MVP
- No heavy web UI.
- No complex multi-tenant platform features.
- No Mac-local runtime or deploy workflow for project validation.
- No custom model training in the first iteration.
- No requirement to run local LLM inference on the same VPS as parsing and storage services.
- No requirement to add OCR to the default ingest path before scanned-PDF evidence justifies it.
- No requirement to adopt ColPali in the first retrieval slice.

## Implementation boundaries
- `src/synapse/cli.py` owns command entry points.
- `src/synapse/server.py` owns the FastAPI app.
- `src/synapse/config.py` owns environment and settings.
- `src/synapse/domain/` owns canonical schema for traceable research artifacts.
- `src/synapse/services/` owns workflow orchestration shared by interfaces.
- `docs/master-roadmap.md` is the source of truth for delivery order.
- `docs/implementation-checklist.md` is the progress ledger.
- `docs/deploy.md` is the canonical server deploy and operations runbook baseline.
- `docs/test-corpus.md` is the source of truth for the external golden PDF set.
- `docs/repo-map.md` is the source of truth for navigation.
