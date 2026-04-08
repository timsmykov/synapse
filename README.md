# Synapse

Synapse is a CLI-first research context layer for systematic reviews and meta-analyses. The initial repository scaffold is aligned to the Notion plan: Python 3.12, Typer CLI, FastAPI control plane, PostgreSQL + pgvector + MinIO + Redis infrastructure, and a repository layout optimized for agent-driven development.

The current baseline now includes the missing architectural seams for Day 1 work: a canonical domain/provenance model, a shared service layer for CLI/API, and reserved package boundaries for ingestion, storage, retrieval, and primitives.

## Scope

- `ingest`: parse scientific PDFs into traceable structured artifacts
- `query`: retrieve document, section, table, formula, and figure context
- `analyze`: run science-specific workflows such as consistency checks and systematic review primitives
- `doctor`: validate server/runtime configuration before heavier integrations land

This scaffold intentionally keeps heavyweight parsing and retrieval integrations out of the critical path. Those adapters belong to the next implementation phases documented in [`docs/architecture.md`](./docs/architecture.md) and [`docs/master-roadmap.md`](./docs/master-roadmap.md).

The most important rule for future work is to keep workflow logic out of entrypoints. `cli.py` and `server.py` should call services; services should use domain models and adapters.

Current execution policy:

- code can be edited from this Mac workspace
- installs, tests, runtime, and deploy verification happen on the server
- current bootstrap/provisioning access is `ssh root@194.163.181.122`
- long-lived deploy commands should move to a dedicated non-root deploy user

Do not treat the Mac as the default runtime environment for Synapse.

## Server-First Start

Use the remote server as the default execution environment. The canonical flow is:

1. edit code locally in this repo
2. push changes to GitHub
3. pull and run them on the server
4. run install/test/runtime commands on the server or inside the server containers

The concrete runbook lives in [`docs/deploy.md`](./docs/deploy.md).

## Repository Guide

- [`Agent.md`](./Agent.md): canonical operating manual for Codex and future agent work
- [`AGENTS.md`](./AGENTS.md): thin agents entrypoint for toolchains that expect it
- [`docs/master-roadmap.md`](./docs/master-roadmap.md): single operational roadmap and phase order
- [`docs/deploy.md`](./docs/deploy.md): canonical server deploy and operations runbook
- [`docs/test-corpus.md`](./docs/test-corpus.md): canonical source and handling rules for golden PDFs
- [`docs/phase-0-verification.md`](./docs/phase-0-verification.md): explicit verification evidence and closeout for Phase 0 baseline
- [`docs/repo-map.md`](./docs/repo-map.md): directory ownership and where new code belongs
- [`docs/agent-prompts.md`](./docs/agent-prompts.md): prompt templates for parallel implementation work
- [`docs/implementation-checklist.md`](./docs/implementation-checklist.md): chronological technical execution checklist
- [`docs/roadmap.md`](./docs/roadmap.md): legacy condensed MVP snapshot, not the execution source of truth

The master execution roadmap lives in [`docs/master-roadmap.md`](./docs/master-roadmap.md). The checkbox ledger lives in [`docs/implementation-checklist.md`](./docs/implementation-checklist.md). Future agents should read both before starting work and mark completed checklist items when they finish their scoped task.

## Planned Infrastructure

- `postgres`: primary store with `pgvector`
- `redis`: queue and transient workflow state
- `minio`: PDF, figure, and artifact object storage
- `app`: FastAPI control plane and server runtime entrypoint

## Current Status

The repository has been reset from the old landing-page codebase and reinitialized as a clean Synapse backend/CLI project. Phase 0 has been explicitly verified, and Phase 1 already includes real single-file and batch JSON ingest, parser adapters, and merge contracts. The next implementation pass should focus on the first quality gate pass on the server against the selected golden corpus.
