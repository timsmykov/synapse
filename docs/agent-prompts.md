# Agent Prompts

Use these prompts when delegating to subagents. Keep tasks narrow and file-scoped.

## Repo scaffold agent
Prompt:
You own only the Python scaffold files. Create a minimal Synapse package with Typer CLI, FastAPI app, settings, and tests. Keep dependencies light and make `--help` and `/health` work.

Expected output:
- `src/synapse/__init__.py`
- `src/synapse/config.py`
- `src/synapse/cli.py`
- `src/synapse/server.py`
- `tests/`

## Ingestion agent
Prompt:
Implement `synapse ingest` for scientific PDFs. Use Docling and GROBID as the primary parsing path and preserve provenance fields such as page, bbox, and confidence. Do not build a full UI.

Expected output:
- Ingestion command
- Parsing adapter layer
- Fixtures or smoke tests

## Storage agent
Prompt:
Design the persistence layer for Postgres 16+, pgvector, MinIO, and Redis. Keep the schema simple and traceable. Prefer JSONB where strict relational modeling is not needed.

Expected output:
- Data access layer
- Schema notes
- Local infra assumptions

## Retrieval agent
Prompt:
Implement the initial retrieval layer with LlamaIndex and hybrid search. Support document, section, table cell, formula, and figure level lookup.

Expected output:
- Index builder
- Query API
- Retrieval tests

## Analysis agent
Prompt:
Add research primitives for systematic reviews. Start with consistency checks, PICO extraction, and table validation. Keep outputs structured and traceable.

Expected output:
- Analysis commands or services
- Structured result models
- Basic verification tests

## Docs agent
Prompt:
Keep the repo docs aligned with the code. Update architecture, roadmap, and repo map when implementation changes.

Expected output:
- Short, actionable doc updates
- No speculative product prose

