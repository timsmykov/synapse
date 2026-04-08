# Synapse

Synapse is a CLI-first research context layer for systematic reviews and meta-analyses. The initial repository scaffold is aligned to the Notion plan: Python 3.12, Typer CLI, FastAPI control plane, PostgreSQL + pgvector + MinIO + Redis infrastructure, and a repository layout optimized for agent-driven development.

## Scope

- `ingest`: parse scientific PDFs into traceable structured artifacts
- `query`: retrieve document, section, table, formula, and figure context
- `analyze`: run science-specific workflows such as consistency checks and systematic review primitives
- `doctor`: validate local configuration before heavier integrations land

This scaffold intentionally keeps heavyweight parsing and retrieval integrations out of the critical path. Those adapters belong to the next implementation phases documented in [`docs/architecture.md`](./docs/architecture.md) and [`docs/roadmap.md`](./docs/roadmap.md).

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e '.[dev]'
cp .env.example .env
docker compose up -d postgres redis minio
synapse doctor
pytest
```

To run the API:

```bash
uvicorn synapse.server:app --reload
```

To inspect the CLI:

```bash
synapse --help
```

## Repository Guide

- [`Agent.md`](./Agent.md): canonical operating manual for Codex and future agent work
- [`docs/repo-map.md`](./docs/repo-map.md): directory ownership and where new code belongs
- [`docs/agent-prompts.md`](./docs/agent-prompts.md): prompt templates for parallel implementation work

## Planned Infrastructure

- `postgres`: primary store with `pgvector`
- `redis`: queue and transient workflow state
- `minio`: PDF, figure, and artifact object storage
- `app`: FastAPI control plane and local development entrypoint

## Current Status

The repository has been reset from the old landing-page codebase and reinitialized as a clean Synapse backend/CLI project. The next implementation pass should focus on the Day 1 ingestion pipeline and corpus evaluation harness.
