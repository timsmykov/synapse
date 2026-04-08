# Phase 0 Verification

Verification date: 2026-04-08

This document records the explicit verification pass for Phase 0 of Synapse: repo foundation, runtime baseline, server-first policy, test corpus contract, and evaluation contract.

## Scope

The verification covered:

- repo structure and architectural seams
- runtime and health/reporting baseline
- server-first deployment policy
- test corpus manifest and evaluation contract
- smoke-level automated validation

## Evidence

Local repo validation:

- `ruff check .`
- `pytest`

Observed result on 2026-04-08:

- `ruff check .` passed
- `pytest` passed with `49 passed`

Remote VPS validation:

- host: `root@194.163.181.122`
- verified `docker` and `docker compose` availability
- verified `/srv/synapse/test_corpus/golden` exists on the server
- verified the current five golden PDFs plus `corpus-manifest.json` are present

## Verified Phase 0 Baseline

The following Phase 0 claims were confirmed:

- old landing/static-site code was replaced with a Synapse backend/CLI scaffold
- Python package baseline exists with `pyproject.toml`, `Dockerfile`, `README`, and console entrypoints
- compose baseline exists for `app`, `postgres`, `redis`, and `minio`
- `.env.example` captures the runtime configuration surface
- canonical `domain` contracts exist for provenance and artifact shapes
- `services` exists as the shared boundary between CLI and API
- package seams exist for `ingest`, `storage`, `retrieval`, and `primitives`
- smoke-level tests exist for config, CLI, runtime health, and service contracts
- `test_corpus/` is defined as manifest/mirror metadata, not as the canonical source of real PDFs
- evaluation contracts exist under `eval/` and are wired into the Python service layer

## Findings Fixed During Verification

The verification found and fixed three baseline drifts:

- `testing` is now treated as a remote server target in [`/Users/timsmykov/Desktop/Synapse/src/synapse/runtime_health.py`](/Users/timsmykov/Desktop/Synapse/src/synapse/runtime_health.py), matching the deploy env templates and VPS policy.
- [`/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py`](/Users/timsmykov/Desktop/Synapse/scripts/evaluate_ingest.py) now defaults to the real corpus manifest instead of the template manifest.
- server-first docs now explicitly distinguish bootstrap `root` access from the future non-root deploy path in [`/Users/timsmykov/Desktop/Synapse/README.md`](/Users/timsmykov/Desktop/Synapse/README.md), [`/Users/timsmykov/Desktop/Synapse/docs/deploy.md`](/Users/timsmykov/Desktop/Synapse/docs/deploy.md), and [`/Users/timsmykov/Desktop/Synapse/docs/test-corpus.md`](/Users/timsmykov/Desktop/Synapse/docs/test-corpus.md).

## Residual Risk

Phase 0 is verified as a solid baseline, but not fully hardened.

Open hardening work remains outside Phase 0:

- dedicated non-root deploy user
- HTTPS and domain-ready reverse proxy path
- backup policy for Postgres and MinIO
- production separation criteria beyond the shared testing VPS

Those items already belong to later checklist items and should not be backfilled into Phase 0.
