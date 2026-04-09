# Synapse Server Deploy

This repository keeps deployment simple on purpose.
The current goal is a single remote server that acts as the default install, test, and runtime environment for Synapse.

## Environment split

- Local Mac: code editing and external PDF source handling only.
- CI: mandatory validation on every push and pull request.
- Remote VPS: default environment for installs, tests, runtime, and multi-service checks.

## Current server policy

- Use the VPS as the canonical Synapse execution environment.
- Treat `root@194.163.181.122` as bootstrap and provisioning access, not as the long-lived deploy identity.
- Move repeatable pull/deploy/check commands to a dedicated non-root deploy user as part of deploy hardening.
- Do not install a local LLM runtime on the box.
- Use API-backed models instead.
- Do not touch Hermes-related containers, ports, or support processes.
- Keep the Synapse stack isolated under its own Docker Compose project name.
- Current bootstrap host: `ssh root@194.163.181.122`

## Files

- `deploy/docker-compose.staging.yml`: testing stack definition
- `deploy/.env.staging.example`: server-side environment template
- `deploy/Caddyfile`: reverse proxy config for the test stack
- `scripts/deploy_staging.sh`: build and launch the stack
- `scripts/check_staging.sh`: health and smoke verification
- `scripts/run_ingest_smoke.sh`: create a tiny PDF fixture and run `synapse ingest`
- `scripts/sync_test_corpus.sh`: sync selected golden PDFs from the external Mac source folder to the server corpus path

## Services in the testing stack

- `caddy`: reverse proxy on loopback high port
- `app`: FastAPI runtime for `/health`, `/ready`, `/info`
- `postgres`: primary database for later storage phases
- `redis`: queue/runtime cache placeholder
- `minio`: object storage for raw PDFs and artifacts
- `grobid`: metadata and citation extraction service

Async worker containers are intentionally not part of this stack yet.
The queue/worker contract belongs to a later phase and should not be faked now.

For the first remote testing rollout, `grobid` is a lightweight stub container on port `8070`.
This keeps the shared VPS setup fast and isolated while the team is still validating the rest of the runtime.
Swap it for a real GROBID image only when remote parser testing becomes necessary.

## Port policy

The testing stack binds only loopback high ports by default:

- `127.0.0.1:18080` -> Caddy
- `127.0.0.1:18000` -> app
- `127.0.0.1:19000` -> MinIO API
- `127.0.0.1:19001` -> MinIO console

This keeps the stack off public interfaces and reduces the chance of colliding with existing software on the server.

## First-time setup

```bash
cp deploy/.env.staging.example deploy/.env.staging
```

Then edit `deploy/.env.staging`:

- set real credentials where needed
- keep `SYNAPSE_LLM_PROVIDER=openai` or another API-backed provider
- leave `OPENAI_API_KEY` empty only if the current task does not need model calls yet
- keep `SYNAPSE_PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu` so the testing image resolves CPU-only PyTorch wheels for `docling`
- keep the default `grobid` stub unless you explicitly need remote GROBID extraction on this box
- change host port values only if they conflict with something already running

## Deploy

```bash
./scripts/deploy_staging.sh
```

The script scopes all operations to the `synapse-testing` Docker Compose project unless overridden via `COMPOSE_PROJECT_NAME`.
Until a non-root deploy user exists, treat this as a controlled bootstrap path rather than the final hardened deploy shape.

## Verify

```bash
./scripts/check_staging.sh
```

This checks:

- container status
- `/health`
- `/ready`
- `/info`
- `python -m synapse doctor` inside the running app container

## Real ingest smoke

```bash
./scripts/run_ingest_smoke.sh
```

This script:

- creates `test_corpus/smoke-fixture.pdf` on the host
- runs `python -m synapse ingest` inside the `app` container
- writes JSON output to `data/ingest-smoke/`

The testing image installs `research` extras by default so Docling is available for this smoke path.
GROBID can stay lightweight on the shared box because the workflow already tolerates metadata failure and continues with Docling-only output.

## Optional SSH tunnel

If the services stay bound to loopback on the server, inspect them through an SSH tunnel:

```bash
ssh -L 18080:127.0.0.1:18080 -L 19001:127.0.0.1:19001 root@194.163.181.122
```

This example uses bootstrap access because that is the currently provisioned identity.
Once a deploy user exists, use that user for routine inspection and deploy operations.

Then open:

- `http://127.0.0.1:18080/health`
- `http://127.0.0.1:19001`

## CI

GitHub Actions runs:

- `ruff check .`
- `pytest`
- `docker compose config`
- `docker build`

This is the validation gate before using the remote testing box.
