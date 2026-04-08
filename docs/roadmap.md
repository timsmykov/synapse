# Synapse Roadmap

Legacy note: this file is a compact MVP snapshot only.
Active execution order lives in `docs/master-roadmap.md`.
Progress tracking lives in `docs/implementation-checklist.md`.

## Goal
Ship a working MVP in 5 days that can ingest scientific PDFs, preserve provenance, and answer traceable research queries from the CLI.

Execution note: edit code wherever convenient, but installs, tests, and runtime happen on the server. The canonical deploy/runbook is `docs/deploy.md`.

## Day 0
- Create the repository skeleton.
- Add `synapse --help`.
- Add Docker Compose for Postgres, pgvector, MinIO, and Redis.
- Prepare a tiny test corpus and an evaluation harness.

## Day 1
- Implement PDF ingestion.
- Wire Docling and GROBID as the primary parsing path.
- Add provenance fields for source page and bbox.
- Make `synapse ingest <pdf>` write structured output.

## Day 2
- Add persistent storage models in Postgres.
- Store raw artifacts in MinIO.
- Add initial indexing with LlamaIndex.
- Add a basic query path over document, section, and table data.

## Day 3
- Add science-specific primitives.
- Start with consistency checks, PICO extraction, and table validation.
- Add one orchestration loop for retry or verification.

## Day 4
- Tighten the CLI surface.
- Add a minimal Python SDK layer if needed.
- Add smoke tests and end-to-end checks.
- Clean up error handling and output formatting.
- Add CI validation for lint, unit, contract, and compose smoke checks.

## Day 5
- Polish docs and examples.
- Run final smoke tests against the test corpus.
- Freeze the MVP scope.
- Prepare the next iteration plan for better retrieval and extraction quality.
- Prepare the first remote testing deploy on a single VPS with isolated compose scope and conservative ingest concurrency.

## Build order
1. Repo skeleton and developer tooling.
2. Ingestion and parsing.
3. Storage and retrieval.
4. Analysis primitives.
5. Tests, docs, and release hardening.

## MVP acceptance
- `docker compose up` starts the server stack.
- `synapse ingest` processes sample PDFs.
- `synapse query` returns traceable results.
- Outputs link back to source documents.
- The system runs self-hosted without external dependencies in the happy path.
- The remote server is the default integrated execution environment.
