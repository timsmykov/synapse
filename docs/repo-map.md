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

## Tests
- `tests/` - unit and integration tests.
- Prefer small tests that validate CLI behavior, config loading, and API health routes.

## Docs
- `docs/architecture.md` - product and technical architecture.
- `docs/roadmap.md` - delivery order and MVP scope.
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
- If a future file is not obvious, update this map.
