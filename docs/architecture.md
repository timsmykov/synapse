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

## Implementation boundaries
- `src/synapse/cli.py` owns command entry points.
- `src/synapse/server.py` owns the FastAPI app.
- `src/synapse/config.py` owns environment and settings.
- `docs/roadmap.md` is the source of truth for delivery order.
- `docs/repo-map.md` is the source of truth for navigation.

