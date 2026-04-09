# Synapse Server Deploy

This repository keeps deployment simple on purpose.
The current goal is a single remote server that acts as the default install, test, and runtime environment for Synapse.

## Environment split

- Local Mac: code editing and external PDF source handling only.
- CI: mandatory validation on every push and pull request.
- Remote VPS: default environment for installs, tests, runtime, and multi-service checks.

Hard rule:

- do not install Synapse runtime dependencies on the Mac as the project execution baseline
- do not run Synapse deploy verification on the Mac
- do not use local Docker Compose on the Mac as a substitute for the VPS
- if a local `.venv` or local runtime artifact is created for this repo, remove it and continue from the server

## Current server policy

- Use the VPS as the canonical Synapse execution environment.
- Treat `root@194.163.181.122` as bootstrap and provisioning access, not as the long-lived deploy identity.
- Move repeatable pull/deploy/check commands to a dedicated non-root deploy user as part of deploy hardening.
- Do not install a local LLM runtime on the box.
- Use API-backed models instead.
- Current model policy: `MiniMax` for the primary LLM path, `OpenRouter` for embeddings and other non-primary models.
- Keep OCR disabled in the default ingest baseline.
- Keep `ColPali` disabled until a later retrieval phase explicitly adopts it.
- Do not touch Hermes-related containers, ports, or support processes.
- Keep the Synapse stack isolated under its own Docker Compose project name.
- Current bootstrap host: `ssh root@194.163.181.122`

Mac prohibition:

- the Mac is not an accepted install/test/deploy target for Synapse
- all install, test, ingest, smoke, and deploy commands belong on the server or inside server containers

## Files

- `deploy/docker-compose.staging.yml`: testing stack definition
- `deploy/.env.staging.example`: server-side environment template
- `deploy/Caddyfile`: reverse proxy config for the test stack
- `scripts/deploy_staging.sh`: build and launch the stack
- `scripts/check_staging.sh`: health and smoke verification
- `scripts/run_ingest_smoke.sh`: create a tiny PDF fixture and run `synapse ingest`
- `scripts/run_golden_ingest.sh`: run real golden PDFs through the running `app` container
- `scripts/evaluate_golden_ingest.sh`: evaluate emitted real-PDF JSON against the golden manifest from the server repo environment
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

The testing stack now uses a real lightweight `grobid` service on port `8070`.
That is necessary because Phase 1 verification now includes real metadata/citation extraction, not just Docling-only fallback behavior.

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
- keep `SYNAPSE_LLM_PROVIDER=minimax`
- set `MINIMAX_API_KEY` for the primary LLM path
- set `OPENROUTER_API_KEY` for embeddings and other non-primary model calls
- leave those API keys empty only if the current task does not need model calls yet
- keep `SYNAPSE_CORPUS_DIR=/srv/synapse/test_corpus` so runtime health and server-side commands point at the canonical corpus location
- keep `SYNAPSE_SERVER_CORPUS_DIR=/srv/synapse/test_corpus` so the `app` container can read the same golden PDFs under the same absolute path as the host
- keep `SYNAPSE_PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cpu` so the testing image preinstalls CPU-only `torch` / `torchvision` wheels before `docling`
- keep `SYNAPSE_PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu` as the auxiliary extra index used during the rest of the research install
- keep `SYNAPSE_GROBID_URL=http://grobid:8070` so the `app` container and isolated helpers use the compose-network service alias
- keep the default lightweight `GROBID_IMAGE` unless you explicitly need a different GROBID build
- keep `SYNAPSE_PARSER_OCR_ENABLED=0` for the MVP baseline
- keep `SYNAPSE_COLPALI_ENABLED=0` until retrieval work explicitly enables it
- change host port values only if they conflict with something already running

## Deploy

```bash
git pull --ff-only origin main
./scripts/deploy_staging.sh
./scripts/run_ingest_smoke.sh
./scripts/check_staging.sh
```

Treat that four-step sequence as the canonical testing-box cycle.
`deploy_staging.sh` rebuilds the `app` image from the current checkout with `--pull --no-cache` and recreates the stack so live container hotpatches do not survive into the next verification pass.
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
- runs `synapse ingest --source ... --output ...` inside the `app` container
- writes JSON output to `data/ingest-smoke/`

The testing image installs `research` extras by default so Docling is available for this smoke path.
GROBID can stay lightweight on the shared box because the workflow already tolerates metadata failure and continues with Docling-only output.
For real golden-fixture verification, run containerized ingest against `/srv/synapse/test_corpus/golden/...`, not the repo-side `test_corpus/` mirror.
Do not treat the `app` container as the canonical place to invoke `scripts/evaluate_ingest.py`: the runtime image does not carry the repo helper scripts under `/workspace/scripts`.
Run evaluation from the server repo checkout instead, using the repo Python environment.

## Golden ingest

```bash
./scripts/run_golden_ingest.sh
```

By default this:

- runs inside the already running `app` container
- reads from `${SYNAPSE_SERVER_CORPUS_DIR}/golden/*.pdf`
- expands the source set on the host and runs one ingest per PDF in sequence
- writes JSON to `data/ingest-golden/`
- writes per-file logs as `data/ingest-golden/run-01.log`, `run-02.log`, and so on

Optional arguments:

```bash
./scripts/run_golden_ingest.sh data/phase1-canary '/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf'
```

Use this script instead of ad-hoc detached containers so the real-PDF path shares the same environment, networking, and `SYNAPSE_GROBID_URL` contract as the canonical `app` runtime.
The sequential host-side loop is also the canonical batch mode for Phase 1 because it keeps per-document failures observable on the shared VPS.

## Isolated golden ingest

```bash
./scripts/run_golden_ingest_isolated.sh
```

Use this helper when you need a one-shot container instead of `docker compose exec app`, but still want the same compose-network DNS contract for `grobid`.

By default this:

- runs a fresh `synapse-testing:latest` container on `${COMPOSE_PROJECT_NAME}_default`
- uses `deploy/.env.staging` for `SYNAPSE_GROBID_URL` and the rest of the runtime env
- mounts `${SYNAPSE_SERVER_CORPUS_DIR}` read-only at the same absolute path inside the container
- writes JSON to `data/ingest-golden-isolated/`

Optional arguments:

```bash
./scripts/run_golden_ingest_isolated.sh \
  data/phase1-canary \
  '/srv/synapse/test_corpus/golden/01-ecommerce-meta-analysis.pdf' \
  synapse-phase1-canary
```

Do not use ad-hoc `docker run ... -e SYNAPSE_GROBID_URL=http://localhost:8070` for parser verification. Outside the compose network, `localhost` points at the isolated container itself, not at the `grobid` service.

## Golden evaluation

```bash
./scripts/evaluate_golden_ingest.sh
```

By default this:

- evaluates `data/ingest-golden/`
- uses `test_corpus/corpus-manifest.json`
- prefers `${ROOT_DIR}/../.venv/bin/python` on the server when available

Optional arguments:

```bash
./scripts/evaluate_golden_ingest.sh data/phase1-canary test_corpus/corpus-manifest.json
```

This is the canonical evaluation path on the testing box.
It runs from the server repo checkout, where both the emitted JSON and the golden manifest are visible under the same filesystem layout used by the verification docs.

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

The CI gate does not change the runtime policy:

- CI validates the repo
- the server executes the stack
- the Mac does not become a fallback runtime
