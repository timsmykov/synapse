# Synapse Agent Guide

This repository is being rebuilt as **Synapse**: a CLI-first research context layer for systematic reviews and meta-analyses.

Future agents working here should treat this file as the canonical repo guide.

## Mission

Build a production-grade, self-hosted pipeline that can ingest scientific PDFs, extract traceable structured evidence, store it with provenance, retrieve it granularity-by-granularity, and expose it through a fast CLI-first workflow.

The product direction from Notion is:

- `CLI-first` primary interface.
- Traceable outputs with page and bbox provenance.
- Open-source-first dependencies where possible.
- Self-hosted by default.
- Practical MVP first, platform later.

## Source Of Truth

Use these as the authoritative product references:

- Notion page `Synapse`
- Notion page `Технический стек`
- Notion page `Pre-launch Checklist`
- Notion page `Roadmap — MVP за 5 дней`

Use local repo docs as implementation mirrors, not as product invention:

- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/repo-map.md`
- `docs/agent-prompts.md`

If repo docs and Notion diverge, pause and align them before coding beyond the immediate task.

## Development Principles

- Optimize for the MVP path in Notion, not for speculative platform work.
- Keep interfaces small, explicit, and scriptable from the terminal.
- Preserve provenance everywhere it matters: source document, page, bbox, confidence, and transform chain.
- Prefer standard library and small dependencies unless the stack explicitly calls for a larger tool.
- Keep heavy integrations behind clear boundaries and optional extras.
- Do not reintroduce the deleted landing-page/static-site codebase.
- Avoid broad refactors unless they are required to unblock the requested task.
- When touching data pipelines, prefer correctness and traceability over cleverness.

## Expected Repo Shape

- `src/synapse/` for the Python package.
- `tests/` for unit and integration tests.
- `docs/` for implementation guidance and repo maps.
- `data/` for local working data and generated artifacts.
- `eval/` for evaluation scripts and metrics.
- `test_corpus/` for sample or golden PDFs.
- `scripts/` for helper scripts and developer utilities.

## Core Stack To Build Against

- Python 3.12.
- Typer or Click for the CLI.
- FastAPI for the service layer when needed.
- PostgreSQL 16+ with JSONB and pgvector.
- MinIO for object storage.
- Redis for async work queues.
- Docling and GROBID for parsing and metadata.
- MinerU or PDF-Extract-Kit for hard PDF extraction cases.
- LlamaIndex for retrieval and indexing.
- LangGraph and Celery for orchestration when the workflow needs it.

Do not assume all of this exists on day one. Build thin seams so the repo can grow into it.

## Commands

Use these as the default local workflow once the scaffold is in place:

- `python -m pytest`
- `python -m synapse --help`
- `python -m synapse ingest --help`
- `python -m synapse query --help`
- `python -m synapse analyze --help`
- `python -m synapse doctor`
- `uvicorn synapse.server:app --reload`
- `docker compose up --build`

If a command is not implemented yet, add the smallest practical stub and document the gap.

## Coding Expectations

- Keep modules short and purpose-built.
- Prefer clear names over compressed abstractions.
- Add tests for new behavior, especially CLI parsing, config loading, and health endpoints.
- Keep error messages actionable.
- Use typed Python where it improves reliability.
- Do not add framework glue that is not yet needed by the MVP.
- Document public entry points and any non-obvious side effects.

## Working Rules For Agents

- Read the relevant Notion source and the local docs before coding.
- Confirm whether work is scaffolding, pipeline logic, or integration glue before choosing a design.
- Edit only the files needed for the task.
- Do not revert unrelated user changes.
- If a change affects provenance, storage, or CLI semantics, update the relevant docs in the same pass.

