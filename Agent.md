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
- `docs/master-roadmap.md`
- `docs/implementation-checklist.md`
- `docs/deploy.md`
- `docs/test-corpus.md`
- `docs/phase-0-verification.md`
- `docs/repo-map.md`
- `docs/agent-prompts.md`

`docs/roadmap.md` may remain as a compact historical snapshot, but it is not the active execution source of truth.

If repo docs and Notion diverge, pause and align them before coding beyond the immediate task.

Current staging/integration target is `ssh root@194.163.181.122`. Treat `root` as provisioning-only access; long-lived deploy scripts and compose operations should move to a dedicated non-root deploy user.
Code may be edited locally, but installs, tests, runtime commands, and deploy verification happen on the server.
Do not create or keep a project-local Synapse runtime on the Mac. No local `.venv`, no local compose verification, no local deploy path.

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
- `src/synapse/domain/` for canonical artifact and provenance models.
- `src/synapse/services/` for shared use cases invoked by CLI and API.
- `src/synapse/ingest/` for parsing and ingestion adapters.
- `src/synapse/storage/` for persistence and object storage adapters.
- `src/synapse/retrieval/` for indexing and query logic.
- `src/synapse/primitives/` for review-specific analysis primitives.
- `tests/` for unit and integration tests.
- `docs/` for implementation guidance and repo maps.
- `data/` for generated artifacts and runtime data.
- `eval/` for evaluation scripts and metrics.
- `test_corpus/` for manifest files, mirrors, and corpus metadata, not as the canonical source of truth for the real PDFs.
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

Current provider policy:

- `MiniMax` is the primary agent/base LLM provider.
- `OpenRouter` is the default path for embeddings and other non-primary model routing.
- Default ingest is `Docling + GROBID` without OCR.
- `ColPali` remains deferred until the retrieval phase.

Do not assume all of this exists on day one. Build thin seams so the repo can grow into it.

## Commands

Use these as the default server-side workflow once the scaffold is in place:

- `python -m pytest`
- `python -m synapse --help`
- `python -m synapse ingest --help`
- `python -m synapse query --help`
- `python -m synapse analyze --help`
- `python -m synapse doctor`
- `uvicorn synapse.server:app --reload`
- `docker compose up --build`

Run them on the server or inside the server containers, not as a required Mac-local setup.
If a local runtime artifact is created on the Mac for convenience, treat it as disposable and remove it.
If a command is not implemented yet, add the smallest practical stub and document the gap.

## Coding Expectations

- Keep modules short and purpose-built.
- Prefer clear names over compressed abstractions.
- Add tests for new behavior, especially CLI parsing, config loading, and health endpoints.
- Add contract tests for domain shapes and service outputs as soon as those layers exist.
- Keep error messages actionable.
- Use typed Python where it improves reliability.
- Do not add framework glue that is not yet needed by the MVP.
- Document public entry points and any non-obvious side effects.

## Roadmap Discipline

- Read `docs/master-roadmap.md` before starting any scoped work.
- Read `docs/implementation-checklist.md` before starting any scoped work.
- Treat `docs/master-roadmap.md` as the master execution roadmap for the repo.
- Treat `docs/implementation-checklist.md` as the progress ledger for checkbox status.
- Before coding, identify which phase and which checklist items your task covers.
- After completing a scoped task, update the relevant checklist items in the same pass.
- After completing a scoped task, proactively update any roadmap, verification, corpus, deploy, repo-map, or architecture docs touched by that work in the same pass; do not wait for a separate reminder.
- If a task spans multiple phases, mark only the items you actually closed and leave the rest open.
- Do not invent new sequencing; follow the dependency order already recorded in the roadmap and checklist.

## Carcass vs Components

Keep the project split between:

- `carcass/scaffold`: repo/runtime integration, contracts, deploy path, docs, and phase verification
- `components`: isolated product modules developed within the current phase

Do not replace the phase model with component-only planning.
The phases in `docs/master-roadmap.md` remain the sequencing mechanism.
Execute each phase through disjoint component workstreams plus one scaffold workstream.

Default scaffold scope:

- `src/synapse/config.py`
- `src/synapse/cli.py`
- `src/synapse/server.py`
- `src/synapse/domain/`
- `src/synapse/services/`
- `deploy/`
- runtime scripts
- roadmap/checklist/verification docs

Default component scope:

- parser adapters in `src/synapse/ingest/`
- parser-specific tests
- merge/eval modules with explicit ownership
- later `storage/`, `retrieval/`, and `primitives/` modules

Scaffold ownership should stay singular.
Do not let multiple agents edit the same integration seam in parallel.

## Working Rules For Agents

- Read the relevant Notion source and the local docs before coding.
- Confirm whether work is scaffolding, pipeline logic, or integration glue before choosing a design.
- Edit only the files needed for the task.
- Do not revert unrelated user changes.
- If a change affects provenance, storage, or CLI semantics, update the relevant docs in the same pass.
- Every agent owns the doc sync for its own slice. Treat roadmap/checklist/verification updates as part of done, not as optional follow-up work.

## Subagent Operating Mode

- Default to aggressive subagent usage whenever work can be parallelized safely.
- Treat the available subagent pool as the default execution model, not as an exception path.
- Use only the frontier `gpt-5.4` model for subagents; do not use `gpt-5.4-mini` or other mini variants.
- Keep the immediate blocking step local, but delegate adjacent exploration, implementation, and verification tasks in parallel.
- Spawn explorer-style subagents to inspect separate areas of the codebase, trace call graphs, review docs, and surface constraints before or during implementation.
- Spawn worker-style subagents for bounded code changes with explicit file ownership whenever multiple edits can proceed independently.
- Prefer multiple narrow subagent tasks over one broad delegated task.
- Give each subagent a concrete deliverable, clear boundaries, and a disjoint write scope whenever possible.
- Tell subagents they are operating in a shared repo and must not revert or overwrite unrelated changes.
- Use subagents for verification passes as well: tests, targeted reviews, regression checks, and doc-sync checks can run in parallel with coding.
- Reuse active subagents when follow-up work stays in the same context, instead of restarting analysis from scratch.
- Do not wait idly on one subagent if another useful task can be delegated or completed locally.
- If a task is large, split it into discovery, implementation, and verification lanes and run them concurrently.
- Only avoid delegation when the task is tiny, fully linear, or so tightly coupled that subagents would add coordination cost.
- Optimize for iteration speed and total throughput across the whole team of agents, not for single-agent neatness.
