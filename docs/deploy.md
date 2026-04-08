# Synapse Server Deploy

This repository keeps deployment simple on purpose.
The current goal is a single remote server that acts as the default install, test, and runtime environment for Synapse.

## Environment split

- Local Mac: code editing and external PDF source handling only.
- CI: mandatory validation on every push and pull request.
- Remote VPS: default environment for installs, tests, runtime, and multi-service checks.

## Current server policy

- Use the VPS as the canonical Synapse execution environment.
- Do not install a local LLM runtime on the box.
- Use API-backed models instead.
- Do not touch Hermes-related containers, ports, or support processes.
- Keep the Synapse stack isolated under its own Docker Compose project name.
- Current host: `ssh root@194.163.181.122`

## Files

- `deploy/docker-compose.staging.yml`: testing stack definition
- `deploy/.env.staging.example`: server-side environment template
- `deploy/Caddyfile`: reverse proxy config for the test stack
- `scripts/deploy_staging.sh`: build and launch the stack
- `scripts/check_staging.sh`: health and smoke verification

## Services in the testing stack

- `caddy`: reverse proxy on loopback high port
- `app`: FastAPI runtime for `/health`, `/ready`, `/info`
- `postgres`: primary database for later storage phases
- `redis`: queue/runtime cache placeholder
- `minio`: object storage for raw PDFs and artifacts
- `grobid`: metadata and citation extraction service

Async worker containers are intentionally not part of this stack yet.
The queue/worker contract belongs to a later phase and should not be faked now.

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
- change host port values only if they conflict with something already running

## Deploy

```bash
./scripts/deploy_staging.sh
```

The script scopes all operations to the `synapse-testing` Docker Compose project unless overridden via `COMPOSE_PROJECT_NAME`.

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

## Optional SSH tunnel

If the services stay bound to loopback on the server, inspect them through an SSH tunnel:

```bash
ssh -L 18080:127.0.0.1:18080 -L 19001:127.0.0.1:19001 root@194.163.181.122
```

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
