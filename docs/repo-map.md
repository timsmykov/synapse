# Repo Map

## Top level
- `README.md` - project overview and quick start.
- `pyproject.toml` - Python package metadata and tooling.
- `docker-compose.yml` - local infrastructure stack.
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
- `docs/deployment.md` - single-node VPS deploy/runbook baseline.
- `docs/roadmap.md` - condensed historical MVP snapshot, not the active execution map.
- `docs/repo-map.md` - navigation guide.
- `docs/agent-prompts.md` - prompt templates for subagents.

## Data and local assets
- `data/` - local runtime data and scratch files.
- `test_corpus/` - sample scientific PDFs for validation.
- `eval/` - evaluation scripts and metrics.

## Working rules
- Do not move implementation logic into docs.
- Keep CLI behavior visible and easy to test.
- Prefer adding one clear module per responsibility instead of large utility files.
- Keep entrypoints thin and route work through `services/` and `domain/`.
- If a future file is not obvious, update this map.
