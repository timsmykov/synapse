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
- Parsing: Docling, GROBID, MinerU or PDF-Extract-Kit where it improves figure and formula extraction
- Storage: PostgreSQL 16+ with JSONB and pgvector, MinIO, Redis
- Retrieval: LlamaIndex with hybrid vector + keyword + metadata search
- Deployment: Docker Compose first, Kubernetes later
- Validation: local pytest/smoke loop plus CI gates plus remote staging

## Environments
- Local development stays on the Mac for the fast inner loop: unit tests, CLI checks, contract tests, and small-scope API smoke tests.
- CI is the mandatory validation gate for lint, unit, contract, and compose smoke checks before deploy.
- Remote staging runs on a single self-hosted VPS with Docker Compose, Postgres, Redis, MinIO, GROBID, and the Synapse app/worker services.
- Current staging host assumption: `ssh root@194.163.181.122` for initial provisioning, followed by a dedicated non-root deploy user.
- Production should move to a separate node once usage or parsing concurrency grows beyond private MVP traffic.
- A single VPS is acceptable for both staging and low-traffic private production only as a temporary step, and only without colocating heavy local LLM inference on the same machine.

## Runtime policy
- Keep the inner development loop local; do not make the VPS the default dev environment.
- Use the remote VPS as the shared integration box for real PDFs, multi-service testing, and manual QA.
- Treat GROBID and document parsing as memory-sensitive workloads; keep ingest concurrency low on the first VPS tier.
- Do not expose Postgres, Redis, or MinIO directly to the public internet.
- Put the public API behind a reverse proxy such as Caddy or Nginx with HTTPS termination.
- Use a non-root deploy user and scripted Docker Compose deploys.

## Code boundaries
- `src/synapse/domain/` owns canonical artifacts, provenance, and request/response models.
- `src/synapse/services/` owns use cases shared by CLI and API.
- `src/synapse/ingest/` owns parser adapters and normalization.
- `src/synapse/storage/` owns Postgres, MinIO, and queue persistence.
- `src/synapse/retrieval/` owns indexes and query assembly.
- `src/synapse/primitives/` owns review-specific analysis primitives.

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
- No Kubernetes dependency for local development.
- No custom model training in the first iteration.
- No requirement to run local LLM inference on the same VPS as parsing and storage services.

## Implementation boundaries
- `src/synapse/cli.py` owns command entry points.
- `src/synapse/server.py` owns the FastAPI app.
- `src/synapse/config.py` owns environment and settings.
- `src/synapse/domain/` owns canonical schema for traceable research artifacts.
- `src/synapse/services/` owns workflow orchestration shared by interfaces.
- `docs/master-roadmap.md` is the source of truth for delivery order.
- `docs/implementation-checklist.md` is the progress ledger.
- `docs/deployment.md` is the VPS deploy and operations runbook baseline.
- `docs/repo-map.md` is the source of truth for navigation.
