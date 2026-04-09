# Repo Map

## Top level
- `README.md` - project overview and quick start.
- `pyproject.toml` - Python package metadata and tooling.
- `docker-compose.yml` - server/runtime infrastructure stack.
- `.env.example` - environment variables.
- `Agent.md` - canonical guide for Codex and any future agent work.

## Source
- `src/synapse/__init__.py` - package entry.
- `src/synapse/config.py` - settings and environment access.
- `src/synapse/cli.py` - Typer commands.
- `src/synapse/server.py` - FastAPI application.
- `src/synapse/domain/` - canonical artifact and provenance models.
- `src/synapse/services/` - shared use cases for CLI and API.
- `src/synapse/ingest/` - parsing and ingestion adapter boundaries.
- `src/synapse/storage/` - persistence and object storage boundaries.
- `src/synapse/retrieval/` - indexing and query boundaries.
- `src/synapse/primitives/` - research-primitives boundaries.

## Tests
- `tests/` - unit and integration tests.
- Prefer small tests that validate CLI behavior, config loading, and API health routes.

## Docs
- `docs/architecture.md` - product and technical architecture.
- `docs/master-roadmap.md` - active execution order and phase status.
- `docs/implementation-checklist.md` - checkbox ledger for execution progress.
- `docs/deploy.md` - canonical server deploy and operations runbook.
- `docs/test-corpus.md` - canonical source and handling rules for the external golden PDF set.
- `docs/roadmap.md` - condensed historical MVP snapshot, not the active execution map.
- `docs/repo-map.md` - navigation guide.
- `docs/agent-prompts.md` - prompt templates for subagents.

## Data and local assets
- `data/` - generated artifacts and runtime data.
- `test_corpus/` - corpus manifests, mirrors, and test metadata; the real golden PDFs live outside the repo.
- `eval/` - evaluation scripts and metrics.

## Runtime rule
- This repo may be edited on the Mac, but Synapse runtime/install/test/deploy execution belongs to the server.
- Do not treat `.venv`, local compose state, or other local runtime artifacts as part of the accepted project workflow.

## Working rules
- Do not move implementation logic into docs.
- Keep CLI behavior visible and easy to test.
- Prefer adding one clear module per responsibility instead of large utility files.
- Keep entrypoints thin and route work through `services/` and `domain/`.
- If a future file is not obvious, update this map.
